"""InteractiveObject class, for plot-ov. Not for direct use, just subclassing.

Classes Line and Cursor subclass InteractiveObject defined here.
Rectangle subclasses Line, so it is a sub-subclass of InteractiveObject
"""

import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like


class InteractiveObject:
    """Base class for moving objects on a figure. Used for subclassing.
    
    The most important method it defines is `update_graph`, which manages
    the motion of objects on the figure. Motion is synchronized using one
    of the moving objects as a `leader`, which needs to be defined in the
    subclasses; only this object to calls `update_graph`. Indeed, the
    latter method has a loop on all `moving_objects` inside of it.
    
    This base class also manages the connection of matplotlib figure events
    through the connect() and disconnect() methods and associated callbacks.
    The callbacks are empty here and those needed have to be defined in the
    subclasses.
    """
    
    name = 'Interactive Object'
    
    blit = True
    all_objects = set()  # tracking all instances of the object
    moving_objects = set()  # objects currently moving on figure
    background = None  # background save for blitting
    initiating_motion = False  # True when the leading object had been selected
    leader = None

    # (leading object is the one that triggers motion of the other selected 
    # objects in the case where there are several objects moving at the same 
    # time. This feature is for synchronizing issues in blitting mode.
    
    # Define default colors of the class (potentially cycled through by some
    # methods. If user specifies a color not in the list, it is added to the
    # class colors.
    white = '#eeeeee' # not completely white so that it is still visible
    black = '#111111' # same in case of black background
    colors = [black, 'r', 'b', 'g', white]

    def __init__(self, fig=None, ax=None, color=None, blit=True):     

        self.fig = plt.gcf() if fig is None else fig
        self.ax = plt.gca() if ax is None else ax

        # This is because adding lines can re-dimension axes limits
        self.xlim = self.ax.get_xlim()
        self.ylim = self.ax.get_ylim()
        
        self.all_objects.add(self)
        
        if color is None:
            self.color = self.__class__.colors[0]
        elif is_color_like(color) == False:
            print('Warning: color not recognized. Falling back to default.')
            self.color = self.__class__.colors[0]
        else:
            self.color = color
            if color not in self.__class__.colors:
                self.__class__.colors.append(color)
                
                # set that stores info about what artists are picked
        self.picked_artists = set() # they can be different frmo the active
        # artists, because e.g. when a line moves as a whole, only the line
        # is picked, but the two edge points need to be moving/active as well.
        
        self.moving = False # indicates whether object is currently moving.
        
        self.press_info = None  # stores useful useful mouse click information

        # the last object to be instanciated dictates if blitting is true or not
        self.__class__.blit = blit


        # this seems to be a generic way to bring window to the front but I
        # have not checked with all backends etc, and it does not always work
        plt.get_current_fig_manager().show()


    def __repr__(self):
        figs = [o.fig for o in self.__class__.all_objects]
        n_on_fig = figs.count(self.fig)
        name = self.__class__.name
        return f'{name} #{n_on_fig} on Fig. {self.fig.number}.'

    def __str__(self):
        name = self.__class__.name
        return f'{name} on Fig. {self.fig.number}.'
    
# ================================== methods =================================
    
    @staticmethod
    def get_pt_position(pt):
        "Gets point position as a tuple, from matplotlib line data"
        xpt = pt.get_xdata()
        ypt = pt.get_ydata()
        x = xpt.item()  # convert numpy array to scalar, faster than unpacking
        y = ypt.item()
        return x, y
    
    
    def update_graph(self, event):
        """Update graph with the moving artists. Called only by the leader."""
        
        x = event.xdata
        y = event.ydata
        
        canvas = self.fig.canvas
        ax = self.ax
        move_initiated = self.__class__.initiating_motion

        if self.__class__.blit is True and move_initiated is True:
            canvas.draw()
            self.__class__.background = canvas.copy_from_bbox(ax.bbox)
            self.__class__.initiating_motion = False

        if self.__class__.blit is True:
            # without this line, the graph keeps all successive positions of
            # the cursor on the screen
            canvas.restore_region(self.__class__.background)

        # now the leader triggers update of all moving artists including itself
        for obj in self.__class__.moving_objects:
            
            # update position data of object depending on its motion mode
            obj.update_position((x, y))
            
            # Draw all artists of the object (if not, some can miss in motion)
            if self.__class__.blit is True:
                for artist in obj.all_artists:
                    ax.draw_artist(artist)

        # without this below, the graph is not updated
        if self.__class__.blit is True:
            canvas.blit(ax.bbox)
        else:
            canvas.draw()


    def update_position(self, position, mode=None):
        """Update object position depending on moving mode and mouse position.
        
        Here it does not do much, but the method needs to be rewritten in
        subclassing to be useful. It is used by update_graph().
        """
        x, y = position
        return x, y, mode
    
    def create(self, options):
        """Create object based on options. Need to be defined in subclass."""
        pass
    
    def delete(self):
        """Delete object by removing its components and references"""
        for artist in self.all_artists:
            artist.remove()
        self.disconnect()
        self.__class__.all_objects.remove(self)
        self.fig.canvas.draw()

    
# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """connect object to figure canvas events"""
        # mouse events
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.cidpick = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)    
        #key events
        self.cidpressk = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        # figure events
        self.cidaxenter = self.fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.cidaxleave = self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.cidclose = self.fig.canvas.mpl_connect('close_event', self.on_close)

   
    def disconnect(self):
        """disconnect callback ids"""    
        # mouse events
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidpick)
        # key events
        self.fig.canvas.mpl_disconnect(self.cidpressk)
        # figure events
        self.fig.canvas.mpl_disconnect(self.cidaxenter)
        self.fig.canvas.mpl_disconnect(self.cidaxleave)
        self.fig.canvas.mpl_disconnect(self.cidclose)


# ============================ callback functions ============================


    # mouse events 
    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_release(self, event):
        pass
    
    def on_pick(self, event):
        pass
 
    def on_motion(self, event):
        pass
    
    # key events
    
    def on_key_press(self, event):
        pass

    # figure events
    
    def on_enter_axes(self, event):
        pass

    def on_leave_axes(self, event):
        pass

    def on_close(self, event):
        pass
    
    


