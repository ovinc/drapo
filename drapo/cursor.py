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
        if self.shape in ('hline', 'vline', 'crosshair'):
            self._draw_lines()
        else:
            self._draw_marker()

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

    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `color` (matplotlib's color, default: None (class default value)).
    - `c` (shortcut for `color`)
    - `linestyle` (matplotlib's linestyle, default: dotted ':').
    - `linewidth` (float, default: 1.0). Line width.
    - `horizontal`: if True (default), display horizontal line of cursor
    - `vertical`: if True (default), display vertical line of cursor
    - `blit` (bool, default: True). Blitting for performance.
    - `show_clicks` (bool, default:False). Mark location of clicks.
    - `record_clicks` (bool, default False). Create a list of click positions.

    The 3 following parameters can be 1, 2, 3 (left, middle, right mouse btns).
    - `mouse_add` (int, default 1). Adds a (x, y) point by clicking.
    - `mouse_pop` (int, default 3). Removes most recently added point.
    - `mouse_stop`(int, default 2). Stops click recording. Same as reaching n.

    The 3 following parameters are useful for ginput-like functions.
    - `n` (int, default 1000). Cursor deactivates after n clicks.
    - `block` (bool, default False). Block console until nclicks is reached.
    - `timeout` (float, default 0, i.e. infinite) timeout for blocking.

    The last 3 parameters customize appearance of click marks when shown.
    - `marker` (matplolib's symbol, default: '+')
    - `marker_size` (matplotlib's markersize, default: None, see below)
    - `marker_style` (matplotlib linestyle, if applicable)

    `marker` can be any matplotlib marker (e.g. 'o', 'x', etc.), but also
    'hline' (full horizontal line), 'vline' (full vertical line), 'crosshair'
    (both vertical and horizontal lines spanning axes). In these last 3
    situations, `marker_size` refers to linewidth, and `marker_style` to the
    linestyle; `marker_style` does not apply to regular matplotlib markers.

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
    commands_color = {'next color': 'shift+right',
                      'previous color': 'shift+left'}

    # keyboard shortcuts to change line width
    commands_width = {'increase width': 'shift+up',
                      'decrease width': 'shift+down'}

    # List of all commands above
    commands_color_or_width = list(commands_color.values()) +\
                              list(commands_width.values())

    # other keyboard shortcuts
    commands_misc = {'add point': 'a',
                     'remove point': 'z',
                     'toggle visibility': ' '}  # space bar

    commands_all = commands_color_or_width + list(commands_misc.values())

    def __init__(self, fig=None, color=None, c=None, linestyle=':', linewidth=1,
                 horizontal=True, vertical=True,
                 blit=True, show_clicks=False, record_clicks=False,
                 mouse_add=1, mouse_pop=3, mouse_stop=2,
                 n=1000, block=False, timeout=0,
                 marker='+', marker_size=None, marker_style='-'):
        """Note: cursor drawn only when the mouse enters axes."""

        super().__init__(fig, color=color, c=c, blit=blit, block=block)

        # Cursor state attributes
        self.press = False  # active when mouse is currently pressed
        self.visible = True  # can be True even if cursor not drawn (e.g. because mouse is outside of axes)
        self.inaxes = False  # True when mouse is in axes

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

        self.fig.canvas.draw()  ## see if useful

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
            pass
            # self.fig.canvas.blit(self.ax.bbox)
        else:
            pass
            # self.fig.canvas.draw()

    def update_position(self, event):
        """Update position of the cursor to follow mouse event."""

        x = event.xdata  # For cursors it is sufficient to work with data coordinates
        y = event.ydata  # (no need to go to pixels as the cursor is always in axes)

        if self.horizontal:
            hline = self.cursor_lines['horizontal']
            hline.set_ydata(y)

        if self.vertical:
            vline = self.cursor_lines['vertical']
            vline.set_xdata(x)

    def reset_after_motion(self):
        pass

    def set_press_info(self, event):
        self.press_info = {'currently pressed': True,
                           'click position': (event.xdata, event.ydata)}

    def erase_marks(self):
        """Erase plotted clicks (marks) without removing click data"""
        for mark in self.marks:
            mark.remove()
        # self.fig.canvas.draw()

    def erase_data(self):
        """Erase data of recorded clicks"""
        self.clickdata = []

    def add_point(self, position):
        """Add point to the click data (triggered by click or key press)"""

        if self.recordclicks:

            self.clickdata.append(position)
            self.clicknumber += 1

        if self.markclicks:

            mark = Marker(self.ax, position, color=self.color,
                          shape=self.markshape, size=self.marksize,
                          style=self.markstyle)
            self.marks.append(mark)

            self._reset_background()

    def remove_point(self):
        """Add point to the click data (triggered by click or key press)"""

        if self.recordclicks:

            if self.clicknumber == 0:
                pass
            else:
                self.clicknumber -= 1
                self.clickdata.pop(-1)  # remove last element

        if self.markclicks:

            if len(self.marks) == 0:
                pass
            else:
                mark = self.marks.pop(-1)
                mark.remove()

            self._reset_background()

    def _reset_background(self):
        """Reset background in blitting mode if markers have been added/removed."""
        canvas = self.fig.canvas
        canvas.draw()
        InteractiveObject.background = canvas.copy_from_bbox(self.ax.bbox)
        canvas.restore_region(InteractiveObject.background)

    def _redraw_cursor(self):
        """Redraw cursor, for use in blitting mode.

        Used to make cursor immediately visible after clicks, or after changes
        of appearance (thickness, color, etc.)
        """
        for obj in InteractiveObject.moving_objects:
            for artist in obj.all_artists:
                self.ax.draw_artist(artist)
        self.fig.canvas.blit(self.ax.bbox)

# ============================= callback methods =============================

    def on_enter_axes(self, event):
        """Create a cursor when mouse enters axes."""
        self.inaxes = True
        self.ax = event.inaxes
        if self.visible:
            self.create(event)
        if InteractiveObject.blit:
            InteractiveObject.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

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
        if self.visible and self.inaxes and not self.press_info['currently pressed']:
            self.update_graph(event)

    def on_mouse_press(self, event):
        """If mouse is pressed, deactivate cursor temporarily."""
        self.set_press_info(event)
        if self.visible and self.inaxes:
            self.erase()

    def on_mouse_release(self, event):
        """When releasing click, reactivate cursor and redraw figure.

        This is in order to accommodate potential zooming/panning.
        """
        self.press_info['currently pressed'] = False
        if self.visible and self.inaxes:
            self.create(event)

        # See if click needs to be recorded / deleted / stopped --------------

        position = (event.xdata, event.ydata)

        # line below avoids recording clicks during panning/zooming
        if position == self.press_info['click position']:

            if event.button == self.clickbutton:
                self.add_point(position)

            elif event.button == self.removebutton:
                self.remove_point()

        if self.clicknumber == self.n or event.button == self.stopbutton:
            print('Cursor disconnected (max number of clicks, or stop button pressed).')
            self.delete()

        if len(InteractiveObject.non_cursor_moving_objects()) == 0:
            print(f'Redrawn by {self}, moving objects: {InteractiveObject.moving_objects}')
            self.fig.canvas.draw()
            InteractiveObject.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
            # self.fig.canvas.restore_region(InteractiveObject.background)
            for artist in self.all_artists:
                self.ax.draw_artist(artist)

        self.fig.canvas.blit(self.ax.bbox)

        # self._redraw_cursor()

    def on_key_press(self, event):
        """Key press controls. Space bar toggles cursor visibility.

        All controls:
            - space bar: toggles cursor visibility
            - up/down arrows: increase or decrease cursor size
            - left/right arrows: cycles through colors
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

# ------------------- recording or removing click data -----------------------

        elif event.key == self.commands_misc['add point']:
            self.add_point((event.xdata, event.ydata))

        # I use 'z' here because backspace (as used in ginput) interferes
        # with the interactive "back" option in matplotlib
        elif event.key == self.commands_misc['remove point']:
            self.remove_point()

# --------------------implement changes on graph -----------------------------

        if event.key in self.commands_color_or_width:
            self.erase()  # easy way to not have to update artist
            self.create(event)

        if event.key in self.commands_all:
            # hack to see changes directly and to prevent display bugs
            # InteractiveObject.initiating_motion = True
            # self.update_graph(event)
            self._redraw_cursor()

# ------------------------ stop if necessary ---------------------------------

        if self.clicknumber == self.n or event.key == 'enter':
            print('Cursor disconnected (max number of clicks, or stop button pressed).')
            self.delete()

    def on_pick(self, event):
        """Contrary to draggble objects, no self-picking here."""
        pass


# =========================== ginput-like function ==========================


def ginput(n=1, timeout=0, show_clicks=True,
           mouse_add=1, mouse_pop=3, mouse_stop=2,
           color=None, c=None, linestyle=':', linewidth=1,
           horizontal=True, vertical=True,
           marker='+', marker_size=None, marker_style='-',
           blit=True):
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

    - color / c (default None, i.e. auto)
    - linestyle (default ':')
    - linewidth (default 1)
    - horizontal (default True)
    - vertical (default True)
    - marker / marker_size / marker_style (click marker appearance)
    - blit (bool, default True)

    Returns
    -------
    List of tuples corresponding to the list of clicked (x, y) coordinates.
    """
    c = Cursor(block=True, record_clicks=True, show_clicks=show_clicks, n=n,
               color=color, c=c, linestyle=linestyle, linewidth=linewidth,
               horizontal=horizontal, vertical=vertical, timeout=timeout,
               mouse_add=mouse_add, mouse_stop=mouse_stop, mouse_pop=mouse_pop,
               marker=marker, marker_size=marker_size, marker_style=marker_style,
               blit=blit)
    data = c.clickdata
    time.sleep(0.2)  # just to have time to see the last click and its mark
    c.erase_marks()
    return data
