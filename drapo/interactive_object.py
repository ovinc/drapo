"""InteractiveObject class. Not for direct use, just subclassing.

Line, Rect and Cursor each subclass the InteractiveObject class defined here.
"""

import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like


def main():
    obj = InteractiveObject()  # For testing purposes
    return obj


class InteractiveObject:
    """Base class for moving objects on a figure. Used for subclassing only.

    See DEVELOPMENT.md for information on how to use this class.
    """

    name = 'Interactive Object'

    all_interactive_objects = []  # tracking all instances of all subclasses
    # (use the all_instances() method to get instances of a single class)
    # This list is returned by the classmethod all_objects().

    moving_objects = set()  # objects currently moving on figure. Includes
    # all subclasses, to be able to manage motion of objects of different
    # classes on the same figure.

    leader = None  # Leader object that synchronizes motion and drawing of all
    # objects when several objects are selected/moving at the same time.
    # This feature is required due to blitting rendering issues.

    initiating_motion = False  # True when the leading object had been selected

    # Attributes for fast rendering of motion with blitting.
    blit = True
    background = None

    # Define default colors of the class (potentially cycled through by some
    # methods. If user specifies a color not in the list, it is added to the
    # class colors.
    colors = ['crimson', 'dimgray', 'whitesmoke', 'dodgerblue', 'lightgreen']

    def __init__(
        self,
        ax=None,
        color=None,
        c=None,
        blit=True,
        block=False,
        verbose=False,
    ):

        self.ax = plt.gca() if ax is None else ax
        self.fig = self.ax.figure

        # Connect matplotlib event handling to callback functions
        self.connect()

        # Tracks instances of any interactive objects of any subclass.
        self.all_interactive_objects.append(self)

        self.all_artists = []  # all artists the object is made of
        self.all_pts = []  # all individual tracking points the object is made of

        # set that stores info about what artists are picked
        self.picked_artists = set()  # they can be different from the active
        # artists, because e.g. when a line moves as a whole, only the line
        # is picked, but the two edge points need to be moving/active as well.

        self.created = False  # True when artists defined, False when erased or not created
        self.moving = False  # faster way to check moving objects than to measure the length of moving_objects
        self.press_info = {'currently pressed': False}  # stores useful useful mouse click information

        # the last object to be instanciated dictates if blitting is true or not
        InteractiveObject.blit = blit
        # Reset leading artist when instanciating a new object
        InteractiveObject.leader = None

        # defines whether the interactive object is blocking the console or not
        self.block = block

        # If verbose is True, various indications are printed in the console
        # when interacting with objects (e.g. 'Cursor deleted', etc.)
        self.verbose = verbose

        # color management ---------------------------------------------------

        if c is not None:
            color = c

        if color is None:
            self.color = InteractiveObject.colors[0]
        elif not is_color_like(color):
            print('Warning: color not recognized. Falling back to default.')
            self.color = InteractiveObject.colors[0]
        else:
            self.color = color
            if color not in InteractiveObject.colors:
                InteractiveObject.colors.append(color)

        # --------------------------------------------------------------------

        # Transforms functions to go from px to data coords.
        # Need to be redefined if figure is resized
        self.datatopx = self.ax.transData.transform  # transform between data coords to px coords.
        self.pxtodata = self.ax.transData.inverted().transform  # pixels to data coordinates

        # this seems to be a generic way to bring window to the front but I
        # have not checked with all backends etc, and it does not always work
        plt.get_current_fig_manager().show()

    def __repr__(self):
        object_list = self.__class__.class_objects()
        objects_on_fig = [obj for obj in object_list if obj.fig == self.fig]
        n_on_fig = len(objects_on_fig)
        try:
            n = objects_on_fig.index(self) + 1
        except ValueError:  # means object has been deleted
            n = 'deleted'
        return f'{self.name} #{n}/{n_on_fig} in Fig. {self.fig.number}.'

    def __str__(self):
        # name = InteractiveObject.name
        # return f'{name} on Fig. {self.fig.number}.'
        return self.__repr__()

# ============================ basic canvas methods ==========================

    def update_background(self):
        """Update background for blitting mode"""
        canvas = self.fig.canvas
        ax = self.ax
        InteractiveObject.background = canvas.copy_from_bbox(ax.bbox)

    def restore_background(self):
        """Restore background, for blitting mode"""
        self.fig.canvas.restore_region(InteractiveObject.background)

    def draw_artists(self):
        """Draw all artists of object, for blitting mode"""
        for artist in self.all_artists:
            self.ax.draw_artist(artist)

    def draw_canvas(self):
        """Draw canvas (expensive)"""
        self.fig.canvas.draw()

    def blit_canvas(self):
        """Blit objects above background, to update animated objects"""
        self.fig.canvas.blit(self.ax.bbox)

# ================================== methods =================================

    def update_graph(self, event):
        """Update graph with the moving artists. Called only by the leader."""

        if InteractiveObject.blit and InteractiveObject.initiating_motion:
            self.draw_canvas()
            self.update_background()
            InteractiveObject.initiating_motion = False

        if InteractiveObject.blit:
            # without this line, the graph keeps all successive positions of
            # the cursor on the screen
            self.restore_background()

        # now the leader triggers update of all moving artists including itself
        for obj in InteractiveObject.moving_objects:

            # update position data of object depending on its motion mode
            obj.update_position(event)

            # Draw all artists of the object (if not, some can miss in motion)
            if InteractiveObject.blit:
                obj.draw_artists()

        # without this below, the graph is not updated
        if InteractiveObject.blit:
            self.blit_canvas()
        else:
            self.draw_canvas()

    def initiate_motion(self, event):
        """Initiate motion and define leading artist that synchronizes plot.

        In particular, if there are several moving objects, save background
        (for blitting) only once. The line selected first becomes the leader
        for moving events, i.e. it is the one that detects mouse moving and
        triggers re-drawing of all other moving lines.
        Note : all moving lines are necesary on the same axes"""

        if InteractiveObject.leader is None:
            InteractiveObject.leader = self
            # Below is to delay background setting for blitting until all
            # artists have been defined as animated.
            # This is because the canvas.draw() and/or canvas_copy_from_bbox()
            # calls need to be made with all moving artists declared as animated
            InteractiveObject.initiating_motion = True

        InteractiveObject.moving_objects.add(self)
        self.moving = True
        if InteractiveObject.blit:
            for artist in self.all_artists:
                artist.set_animated(True)

        # find which elements need to be active/updated during mouse motion
        # and motion mode (defined in subclasses)
        self.set_active_info()
        # store location of pts and of click, and create dict of px pos data for motion
        # (defines self.press_info and self.moving_positions)
        self.set_press_info(event)

        # Transforms functions to go from px to data coords.
        # Need to be redefined if figure is resized or if zooming occurs
        self.datatopx = self.ax.transData.transform  # transform between data coords to px coords.
        self.pxtodata = self.ax.transData.inverted().transform  # pixels to data coordinates

    def reset_after_motion(self):
        """Reset attributes that should be active only during motion."""

        self.picked_artists = set()
        self.active_info = {}
        self.press_info = {'currently pressed': False}
        self.moving_positions = {}
        self.moving = False

        if InteractiveObject.blit:
            for artist in self.all_artists:
                artist.set_animated(False)

        # Reset class variables that store moving information
        InteractiveObject.moving_objects.remove(self)
        if self is InteractiveObject.leader:
            InteractiveObject.leader = None

        # Once all motion has stopped (i.e. no more moving objects that are not
        # a cursor -- by definition, cursor is always moving), redraw figure
        # and add the objects (now stopped) to the blitting background
        # This allows us to call draw() only once even if several objects were
        # moving
        if len(InteractiveObject.non_cursor_moving_objects()) == 0:
            self.draw_canvas()
            if InteractiveObject.blit:
                self.update_background()

    def set_press_info(self, event):
        """Records information related to the mouse click, in px coordinates."""

        press_info = {'click': (event.x, event.y)}  # record click position
        press_info['currently pressed'] = True

        moving_positions = {}

        for pt in self.all_pts:
            xpt, ypt = self.get_pt_position(pt, 'px')
            press_info[pt] = xpt, ypt  # position of all object pts during click
            moving_positions[pt] = xpt, ypt  # will be updated during motion

        self.press_info = press_info
        self.moving_positions = moving_positions

    def erase(self):
        """Lighter than delete(), keeps object connected and referenced"""
        for artist in self.all_artists:
            artist.remove()
        self.all_artists = []

        if self.name == 'Cursor' and InteractiveObject.blit:
            # Cursor is always blitting so it suffices to restore background
            # without re-drawing
            self.restore_background()
            self.blit_canvas()

        else:
            self.draw_canvas()
            if InteractiveObject.blit:
                self.update_background()

        # Below, check if Useful ???
        # Check if object is listed as still moving, and remove it.
        moving_objects = InteractiveObject.moving_objects
        if self in moving_objects:
            moving_objects.remove(self)

        self.created = False

    def delete(self):
        """Hard delete of object by removing its components and references"""
        self.erase()
        InteractiveObject.all_interactive_objects.remove(self)
        self.disconnect()
        if self.block:
            self.fig.canvas.stop_event_loop()

    def delete_others(self, *args):
        """Delete other instances of the same class (eccluding parents/children)

        Options 'all', 'fig', 'ax'. If no argument, assumes 'all'.
        """
        if len(args) == 0:
            option = 'all'
        else:
            option, *_ = args

        all_instances = InteractiveObject.class_objects()

        if option == 'all':
            instances = all_instances
        elif option == 'fig':
            instances = [obj for obj in all_instances if obj.fig == self.fig]
        elif option == 'ax':
            instances = [obj for obj in all_instances if obj.ax == self.ax]
        else:
            raise ValueError(f"{option} is not a valid argument for delete_others(). "
                             "Possible values: 'all', 'fig', 'ax'.")

        others = set(instances) - {self}
        for other in others:
            other.delete()

    def get_pt_position(self, pt, option='data'):
        """Gets point position as a tuple from matplotlib line object.

        Options : 'data' (axis data coords, default) or 'px' (pixel coords).
        """
        # if orig=True (default), the format is not always consistent
        xpt, ypt = pt.get_data(orig=False)
        # convert numpy array to scalar, faster than unpacking
        pos = xpt.item(), ypt.item()
        if option == 'data':
            return pos
        elif option == 'px':
            pos_px = self.datatopx(pos)
            return pos_px
        else:
            raise ValueError(f'{option} not a valid argument.')

    @classmethod
    def class_objects(cls):
        """Return all instances of a given class, excluding parent class."""
        # note : isinstance(obj, class) would also return the parent's objects
        return [obj for obj in cls.all_objects() if type(obj) is cls]

    @classmethod
    def all_objects(cls):
        """Return all interactive objects, including parents and subclasses."""
        return cls.all_interactive_objects

    @classmethod
    def cursor_moving_objects(cls):
        return [obj for obj in cls.moving_objects if obj.name == 'Cursor']

    @classmethod
    def non_cursor_moving_objects(cls):
        """Objects currently moving but which are not cursor"""
        return set(cls.moving_objects) - set(cls.cursor_moving_objects())

    @classmethod
    def clear(cls):
        """Delete all interactive objects of the class and its subclasses."""
        objects = [obj for obj in cls.all_objects()]  # needed to avoid iterating over decreasing set
        for obj in objects:
            obj.delete()

# TO DEFINE IN SUBCLASSES ====================================================

    def create(self):
        """Create object based on options. Need to be defined in subclass."""
        pass

    def set_active_info(self):
        """Store information useful when in motion. Defined in subclasses."""
        active_info = {}
        return active_info

    def update_position(self, event):
        """Update object position depending on moving mode and mouse position.

        Used by update_graph.
        """
        pass

# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """connect object to figure canvas events"""
        # mouse events
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event',
                                                    self.on_mouse_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event',
                                                      self.on_mouse_release)
        self.cidpick = self.fig.canvas.mpl_connect('pick_event',
                                                   self.on_pick)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event',
                                                     self.on_motion)
        # key events
        self.cidpressk = self.fig.canvas.mpl_connect('key_press_event',
                                                     self.on_key_press)
        self.cidreleasek = self.fig.canvas.mpl_connect('key_release_event',
                                                       self.on_key_release)
        # figure events
        self.cidfigenter = self.fig.canvas.mpl_connect('figure_enter_event',
                                                       self.on_enter_figure)
        self.cidfigleave = self.fig.canvas.mpl_connect('figure_leave_event',
                                                       self.on_leave_figure)
        self.cidaxenter = self.fig.canvas.mpl_connect('axes_enter_event',
                                                      self.on_enter_axes)
        self.cidaxleave = self.fig.canvas.mpl_connect('axes_leave_event',
                                                      self.on_leave_axes)
        self.cidclose = self.fig.canvas.mpl_connect('close_event',
                                                    self.on_close)
        self.cidresize = self.fig.canvas.mpl_connect('resize_event',
                                                     self.on_resize)

    def disconnect(self):
        """disconnect callback ids"""
        # mouse events
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidpick)
        # key events
        self.fig.canvas.mpl_disconnect(self.cidpressk)
        self.fig.canvas.mpl_disconnect(self.cidreleasek)
        # figure events
        self.fig.canvas.mpl_disconnect(self.cidfigenter)
        self.fig.canvas.mpl_disconnect(self.cidfigleave)
        self.fig.canvas.mpl_disconnect(self.cidaxenter)
        self.fig.canvas.mpl_disconnect(self.cidaxleave)
        self.fig.canvas.mpl_disconnect(self.cidclose)
        self.fig.canvas.mpl_disconnect(self.cidresize)

# ============================= callback methods =============================

    # mouse events  ----------------------------------------------------------

    def on_pick(self, event):
        """If picked, save picked objects, or delete objects if right click"""
        selected = event.artist

        if selected not in self.all_artists:
            return

        if event.mouseevent.button == 3:  # right click
            self._on_right_pick()
            return

        self.picked_artists.add(selected)

    def _on_right_pick(self):
        """"What to do when picked with right click"""
        self.delete()

    def on_mouse_press(self, event):
        """When mouse button is pressed, initiate motion."""
        if len(self.picked_artists) == 0:
            return
        else:
            self.initiate_motion(event)

    def on_motion(self, event):
        """Leader artist triggers graph update based on mouse position"""
        if not self.moving:
            return
        # only the leader triggers moving events (others drawn in update_graph)
        if InteractiveObject.leader is self:
            self.update_graph(event)

    def on_mouse_release(self, event):
        """When mouse released, reset attributes to non-moving"""
        if self in InteractiveObject.moving_objects:
            self.reset_after_motion()

    # key events  ------------------------------------------------------------

    def on_key_press(self, event):
        print(f'Key Press: {event.key}')  # For testing purposes
        pass

    def on_key_release(self, event):
        pass

    # figure events  ---------------------------------------------------------

    def on_enter_figure(self, event):
        pass

    def on_leave_figure(self, event):
        pass

    def on_enter_axes(self, event):
        pass

    def on_leave_axes(self, event):
        pass

    def on_resize(self, event):
        """When resizing, re-adjust the conversion from pixels to data pts."""
        # Transforms functions to go from px to data coords.
        # Need to be redefined if figure is resized or if zooming occurs
        self.datatopx = self.ax.transData.transform  # transform between data coords to px coords.
        self.pxtodata = self.ax.transData.inverted().transform  # pixels to data coordinates

    def on_close(self, event):
        """Delete object if figure is closed"""
        self.delete()



if __name__ == '__main__':
    main()
