""" Extensions to Matplotlib: Cursor class, and ginput function.

This module contains a Cursor class (cursor that moves with the mouse) and
a ginput function similar to the matplotlib ginput, but with a cursor
and allowing zooming/panning.
"""

# TODO - To allow cursor to appear on multiple figures, it is necessary to
# connect figure events to callbacks for every existing figure --> do a figure list
# and connect one by one.

# TODO -- add option to pick exact already drawn datapoints close to the click


import time

from .interactive_object import InteractiveObject


class Marker:
    """Markers of different shapes to mark clicks in Matplotlib axes."""

    def __init__(self, ax, position, color, shape, size, style):
        """Create marker in axes at given position.

        Parameters
        ----------
        - ax: Matplotlib axes in which to draw the marker
        - position: (x, y) in data coordinates
        - color
        - shape: can be any matplotlib marker (e.g. '+', 'o', etc.), but also:
            * 'hline': horizontal line spanning axes
            * 'vline': vertical line spanning axes
            * 'crosshair': vertical + horizontal line spanning axes
        - size: size of marker, or linewidth for 'hline', 'vline', 'crosshair'
        - style: only applicable to 'hline', 'vline', 'crosshair' (linestyle)
        """
        self.ax = ax
        self.position = position
        self.color = color
        self.shape = shape
        self.size = size
        self.style = style

        self.artists = []
        self.draw()

    def draw(self):
        """Create marker"""
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        if self.shape in ('hline', 'vline', 'crosshair'):
            self._draw_lines()
        else:
            self._draw_marker()

        self.ax.set_xlim(xmin, xmax)   # prevents auto redefining axes limits
        self.ax.set_ylim(ymin, ymax)   # when drawing marker

    def _draw_lines(self):
        """Draw one or more infinite lines"""
        x, y = self.position
        linewidth = 1 if self.size is None else self.size

        if self.shape in ('hline', 'crosshair'):
            line = self.ax.axhline(y=y, color=self.color, linewidth=linewidth,
                                   linestyle=self.style)
            self.artists.append(line)

        if self.shape in ('vline', 'crosshair'):
            line = self.ax.axvline(x=x, color=self.color, linewidth=linewidth,
                                   linestyle=self.style)
            self.artists.append(line)

    def _draw_marker(self):
        """Draw one single marker"""
        marker, = self.ax.plot(*self.position, color=self.color,
                               marker=self.shape, markersize=self.size)
        self.artists.append(marker)

    def remove(self):
        """Erase marker"""
        for artist in self.artists:
            artist.remove()

class Cursor(InteractiveObject):
    """Cursor following the mouse on any axes of a matplotlib figure.

    Interactive cursor appearance:
    - space bar to toggle visibility (on/off)
    - shift + up/down arrows: increase or decrease width (linewidth)
    - shift + left/right arrows: cycle through different cursor colors

    Interactively extracting figure data:
    - 'a' or left click to add point
    - 'z' or right click to remove point
    - 'enter' or middle click for stopping

    Parameters
    ----------
    All parameters optional so that a cursor can be created by `Cursor()`.

    - `ax` (matplotlib axes, default: current axes, specified as None).
      (Note: Cursor can move on other axes of the same figure)
    - `color` (matplotlib's color, default: None (class default value)).
    - `c` (shortcut for `color`)
    - `linestyle` (matplotlib's linestyle, default: dotted ':').
    - `linewidth` (float, default: 1.0). Line width.
    - `horizontal`: if True (default), display horizontal line of cursor
    - `vertical`: if True (default), display vertical line of cursor
    - `blit` (bool, default: True). Blitting for performance.
    - `show_clicks` (bool, default:False). Mark location of clicks.
    - `record_clicks` (bool, default False). Create a list of click positions.
    - `visible` (bool, default True). If false, cursor initially not visible.

    The 3 following parameters can be 1, 2, 3 (left, middle, right mouse btns).
    - `mouse_add` (int, default 1). Adds a (x, y) point by clicking.
    - `mouse_pop` (int, default 3). Removes most recently added point.
    - `mouse_stop`(int, default 2). Stops click recording. Same as reaching n.

    The 3 following parameters customize appearance of click marks when shown.
    - `marker` (matplolib's symbol, default: '+')
    - `marker_size` (matplotlib's markersize, default: None, see below)
    - `marker_style` (matplotlib linestyle, if applicable)

    `marker` can be any matplotlib marker (e.g. 'o', 'x', etc.), but also
    'hline' (full horizontal line), 'vline' (full vertical line), 'crosshair'
    (both vertical and horizontal lines spanning axes). In these last 3
    situations, `marker_size` refers to linewidth, and `marker_style` to the
    linestyle; `marker_style` does not apply to regular matplotlib markers.

    These last parameters are useful for ginput-like functions.
    - `n` (int, default 1000). Cursor deactivates after n clicks.
    - `block` (bool, default False). Block console until nclicks is reached.
    - `verbose` (bool, default False). If True, some events associated with
                interactive objects are printed in the console.
    - `timeout` (float, default 0, i.e. infinite) timeout for blocking.

    Useful class methods
    --------------------
    - `erase_marks()`: erase click marks on the plot.
    - `erase_data()`: reset recorded click data.

    Useful class attributes
    -----------------------
    - `fig`: matplotlib figure the cursor is active in. Fixed.
    - `ax`: matplotlib axes the cursor is active in. Changes in subplots.
    - `visible`: bool, sets whether cursor drawn or not when in axes.
    - `inaxes`: book, true when mouse (and thus cursor) is in axes
    - `clicknumber`: track the number of recorded clicks.
    - `clickdata`: stores the (x, y) data of clicks in a list.
    - `marks`: list of matplotlib artists containing all click marks drawn.
    """

    name = 'Cursor'

    # keyboard shortcuts to change color
    commands_color = {'next color': 'alt+right',
                      'previous color': 'alt+left'}

    # keyboard shortcuts to change line width
    commands_width = {'increase width': 'alt+up',
                      'decrease width': 'alt+down'}

    # List of all commands above
    commands_color_or_width = list(commands_color.values()) +\
                              list(commands_width.values())

    # other keyboard shortcuts
    commands_misc = {'add point': 'a',
                     'remove point': 'z',
                     'toggle visibility': ' ',  # space bar
                     'stop': 'enter'}

    commands_all = commands_color_or_width + list(commands_misc.values())

    def __init__(self, ax=None, color=None, c=None,
                 linestyle=':', linewidth=1,
                 horizontal=True, vertical=True,
                 blit=True, visible=True,
                 show_clicks=False, record_clicks=False,
                 mouse_add=1, mouse_pop=3, mouse_stop=2,
                 marker='+', marker_size=None, marker_style='-',
                 n=1000, block=False, verbose=False, timeout=0,
                 ):
        """Note: cursor drawn only when mouse enters axes."""

        super().__init__(ax=ax,
                         color=color,
                         c=c,
                         blit=blit,
                         block=block,
                         verbose=verbose)

        # Cursor state attributes
        self.press = False    # active when mouse is currently pressed
        self.visible = visible  # can be True even if cursor not drawn (e.g. because mouse is outside of axes)
        self.inaxes = False   # True when mouse is in axes

        # Appearance options
        self.style = linestyle
        self.width = linewidth
        self.markshape = marker
        self.marksize = marker_size
        self.markstyle = marker_style
        self.horizontal = horizontal
        self.vertical = vertical

        # Recording click options
        self.markclicks = show_clicks
        self.recordclicks = record_clicks
        self.clickbutton = mouse_add
        self.removebutton = mouse_pop
        self.stopbutton = mouse_stop

        # Recording click data
        self.clicknumber = 0  # tracks the number of clicks
        self.n = n  # maximum number of clicks, after which cursor is deactivated
        self.clickdata = []  # stores the (x, y) data of clicks in a list
        self.marks = []  # list containing all artists drawn

        # the blocking option below needs to be after connect()
        if self.block:
            self.fig.canvas.start_event_loop(timeout=timeout)

    def __repr__(self):

        base_message = f'{self.name} on Fig. {self.fig.number}.'

        if self.clickbutton == 1:
            button = "left"
        elif self.clickbutton == 2:
            button = 'middle'
        elif self.clickbutton == 3:
            button = 'right'
        else:
            button = 'unknown'

        if self.markclicks:
            add_message = f"Leaves '{self.markshape}' marks when {button} mouse button is pressed. "
        else:
            add_message = ''

        if self.recordclicks:
            add_message += f'Positions of clicks with the {button} button is recorded in the clickdata attribute.'
        else:
            add_message += 'Positions of clicks not recorded.'

        return base_message + ' ' + add_message

# =========================== main cursor methods ============================

    def create(self, event):
        """Draw a cursor (h+v lines) that stop at the edge of the axes."""
        self.created = True

        ax = self.ax
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        self.delete_others('fig')  # delete all other existing cursors on the figure

        x, y = event.xdata, event.ydata

        # horizontal and vertical cursor lines, the animated option is for blitting

        self.cursor_lines = {}

        if self.horizontal:
            hline = ax.axhline(y=y, color=self.color,
                               linewidth=self.width, linestyle=self.style,
                               animated=InteractiveObject.blit)
            self.cursor_lines['horizontal'] = hline

        if self.vertical:
            vline = ax.axvline(x=x, color=self.color,
                               linewidth=self.width, linestyle=self.style,
                               animated=InteractiveObject.blit)
            self.cursor_lines['vertical'] = vline

        # because plotting the lines can change the initial xlim, ylim
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        self.all_artists = tuple(self.cursor_lines.values())
        # Note: addition to all_objects is made automatically by InteractiveObject parent class
        InteractiveObject.moving_objects.add(self)

        # Below is for cursor to be visible upon creation
        if InteractiveObject.blit:
            self.update_background()   # for first instantiation or after pan/zoom
            self.draw_artists()        # for cursor to be immediately visible
            self.blit_canvas()         # for renrering artists on background
        else:
            self.draw_canvas()

    def update_position(self, event):
        """Update position of the cursor to follow mouse event."""

        x = event.xdata  # For cursors it is sufficient to work with data coordinates
        y = event.ydata  # (no need to go to pixels as the cursor is always in axes)

        if self.horizontal:
            hline = self.cursor_lines['horizontal']
            hline.set_ydata([y])

        if self.vertical:
            vline = self.cursor_lines['vertical']
            vline.set_xdata([x])

    def reset_after_motion(self):
        pass

    def set_press_info(self, event):
        self.press_info = {'currently pressed': True,
                           'motion type': None,
                           'click position': (event.xdata, event.ydata),
                           'xlim': self.ax.get_xlim(),
                           'ylim': self.ax.get_ylim()}

# ========== Manage drawing/recording of clicks (e.g. for ginput()) ==========

    def erase_marks(self):
        """Erase plotted clicks (marks) without removing click data"""
        for mark in self.marks:
            mark.remove()

    def erase_data(self):
        """Erase data of recorded clicks"""
        self.clickdata = []

    def _record_click(self, position):
        """Record click data"""
        self.clickdata.append(position)
        self.clicknumber += 1

    def _unrecord_click(self):
        """Cancel click recording"""
        if self.clicknumber == 0:
            pass
        else:
            self.clicknumber -= 1
            self.clickdata.pop(-1)  # remove last element

    def _draw_click(self, position):
        """Create click drawing"""
        mark = Marker(self.ax, position, color=self.color,
                      shape=self.markshape, size=self.marksize,
                      style=self.markstyle)
        self.marks.append(mark)

    def _undraw_click(self):
        """Cancel click drawing"""
        if len(self.marks) == 0:
            pass
        else:
            mark = self.marks.pop(-1)
            mark.remove()

    def manage_click(self, event):
        """Manage what happens after a legit click (i.e. not for panning/zooming)"""
        position = event.xdata, event.ydata

        if None in position:
            return  # click / key press was made with mouse outside of axes

        # Find if one needs to add or remove a point, and manage cases where
        # the event can come from a mouse event or a key event ---------------

        try:
            add = (event.button == self.clickbutton)
            rem = (event.button == self.removebutton)
        except AttributeError:
            add = (event.key == self.commands_misc['add point'])
            rem = (event.key == self.commands_misc['remove point'])
        finally:
            if not (add or rem):  # both are false, do nothing
                return

        if self.recordclicks:

            self._record_click(position) if add else self._unrecord_click()
            if self.verbose:
                print('click recorded')

        if self.markclicks:

            self._draw_click(position) if add else self._undraw_click()

            self.draw_canvas()             # redraw to add/remove click mark
            if InteractiveObject.blit:
                self.update_background()   # store this as new background for blitting
                self.blit_canvas()         # this makes cursor reappear

# ============================= callback methods =============================

    def on_enter_axes(self, event):
        """Create a cursor when mouse enters axes."""
        self.inaxes = True
        self.ax = event.inaxes
        if self.visible and not self.press_info['currently pressed']:
            self.create(event)

    def on_leave_axes(self, event):
        """Erase cursor when mouse leaves axes."""
        self.inaxes = False
        if self.visible and not self.press_info['currently pressed']:
            self.erase()

    def on_motion(self, event):
        """Update position of the cursor when mouse is in motion.

        Do nothing if pressed to avoid weird interactions with panning.
        Note that update_graph() is not called when other interactive objects
        are moving (and thus when a leader is already updating the graph),
        because this happens only when the mouse is currently pressed.
        """
        # In case one missed the entry of mouse in axes (e.g. because Cursor
        # instantiated while mouse was already in axes)
        if not self.inaxes and event.inaxes:
            self.inaxes = True

        # If currently pressed, determine if it's pressed with other moving
        # objects (dragging mode), or pressed with no other objects moving
        # (i.e. panning/zooming or clicking for ginput with slight motion)
        if self.press_info['currently pressed'] and self.press_info['motion type'] is None:
            if len(InteractiveObject.non_cursor_moving_objects()) > 0:
                self.press_info['motion type'] = 'multi'
            else:
                self.press_info['motion type'] = 'solo'

        # If not currently pressed, check if creating a Cursor is needed and
        # update cursor position during motion.
        if not self.press_info['currently pressed'] and self.visible and self.inaxes:

            # Below is to tackle the case where Cursor() is called when the mouse
            # is already in axes
            if not self.created:
                self.create(event)

            # Below is regular updating of graph to take into account cursor motion
            self.update_graph(event)

    def on_mouse_press(self, event):
        """If mouse is pressed, deactivate cursor temporarily.

        This is in order to accommodate potential zooming/panning.
        """
        self.set_press_info(event)
        if self.visible and self.inaxes:
            self.erase()

    def on_mouse_release(self, event):
        """When releasing click, reactivate cursor and redraw figure if necessary."""

        # Detect if the release is due to panning/zooming --------------------

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # The try/except block solves a bug when cursor is instanciated when
        # mouse is already in axes and 'xlim' is not defined in press_info
        # (I'm not sure I completely understand why it happens)
        try:
            xlim_saved = self.press_info['xlim']
            ylim_saved = self.press_info['ylim']
        except KeyError:
            pan_zoom = False
        else:
            # if axes limits have changed, zoom/pan must have occured
            pan_zoom = False if (xlim == xlim_saved and ylim == ylim_saved) else True

        # Update dictionary used to store press/motion info ------------------

        self.press_info = {'currently pressed': False}

        # See if click needs to be recorded / deleted  (in case of a legit
        # click) or if background needs to be updated (in case of pan/zoom)

        if not pan_zoom:
            self.manage_click(event)
        else:
            if InteractiveObject.blit:
                self.blit_canvas()  # I don't know why it does not work if I
                # don't put this here ...

        # See if cursor needs to re-appear or be deleted etc. ----------------

        if self.clicknumber == self.n or event.button == self.stopbutton:
            if self.verbose:
                print('Cursor disconnected (max number of clicks, or stop button pressed).')
            self.delete()

        elif self.visible and self.inaxes:
            self.create(event)

    def on_key_press(self, event):
        """Key press controls. Space bar toggles cursor visibility.

        All controls:
            - space bar: toggles cursor visibility
            - Alt + up/down arrows: increase or decrease cursor size
            - Alt + left/right arrows: cycles through colors
            - "a" : add point
            - "z" : cancel last point
            - enter : stop recording
        """
# ----------------- changes in appearance of cursor --------------------------

        if event.key == self.commands_misc['toggle visibility']:  # Space Bar
            if self.inaxes:  # create or delete cursor only if it's in axes
                self.erase() if self.visible else self.create(event)
            self.visible = not self.visible  # always change visibility status

        elif event.key == self.commands_width['increase width']:
            self.width += 0.5

        elif event.key == self.commands_width['decrease width']:
            self.width = self.width - 0.5 if self.width > 0.5 else 0.5

        elif event.key in self.commands_color.values():
            # finds at which position the current color is in the list
            colorindex = InteractiveObject.colors.index(self.color)
            if event.key == self.commands_color['next color']:
                colorindex += 1
            else:
                colorindex -= 1
            colorindex = colorindex % len(InteractiveObject.colors)
            self.color = InteractiveObject.colors[colorindex]

        if event.key in self.commands_color_or_width:
            self.erase()  # easy way to not have to update artist
            self.create(event)

# ------------------- recording or removing click data -----------------------

        elif event.key in (self.commands_misc['add point'],
                           self.commands_misc['remove point']):
            self.manage_click(event)

# ------------------------ stop if necessary ---------------------------------

        if self.clicknumber == self.n or event.key == self.commands_misc['stop']:
            if self.verbose:
                print('Cursor disconnected (max number of clicks, or stop button pressed).')
            self.delete()

    def on_pick(self, event):
        """Contrary to draggable objects, no self-picking here."""
        pass


# =========================== ginput-like function ==========================


def ginput(n=1, timeout=0, show_clicks=True,
           mouse_add=1, mouse_pop=3, mouse_stop=2,
           color=None, c=None, linestyle=':', linewidth=1,
           horizontal=True, vertical=True,
           marker='+', marker_size=None, marker_style='-',
           cursor=True, blit=True, ax=None, verbose=False):
    """Improved ginput function (graphical data input) compared to Matplotlib's.

    In particular, a cursor helps for precise clicking and zooming/panning
    do not add extra click data.

    Key shortcuts and mouse clicks follow the Cursor class behavior,
    in particular the key shortcuts are `a`, `z`, `enter` instead of
    any key, backspace and enter. See Cursor class documentation for more info.
    All Cursor class interactive features are usable.

    Parameters
    ----------
    Parameters are exactly the same as matplotlib.pyplot.ginput, see
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ginput.html
    with the following additional parameters (see drapo.Cursor):

    - `color` / c (default None, i.e. auto)
    - `linestyle` (default ':')
    - `linewidth` (default 1)
    - `horizontal` (default True)
    - `vertical` (default True)
    - `marker` / `marker_size` / `marker_style` (click marker appearance)
    - `cursor` (if False, do not show cursor initially; default True)
    - `blit` (bool, default True: use blitting for faster rendering)
    - `ax` (default None, i.e. last active axes)
    - `verbose` (bool, default False). If True, some events associated with
                interactive objects are printed in the console.

    Returns
    -------
    List of tuples corresponding to the list of clicked (x, y) coordinates.
    """
    c = Cursor(block=True, record_clicks=True, show_clicks=show_clicks, n=n,
               color=color, c=c, linestyle=linestyle, linewidth=linewidth,
               horizontal=horizontal, vertical=vertical, timeout=timeout,
               mouse_add=mouse_add, mouse_stop=mouse_stop, mouse_pop=mouse_pop,
               marker=marker, marker_size=marker_size, marker_style=marker_style,
               blit=blit, visible=cursor, ax=ax, verbose=verbose)
    data = c.clickdata
    time.sleep(0.2)  # just to have time to see the last click and its mark
    c.erase_marks()
    return data
