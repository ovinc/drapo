""" Extensions to Matplotlib: Cursor class, and ginput function.

This module contains a Cursor class (cursor that moves with the mouse) and
a ginput function identical to the matplotlib ginput, but with a cursor.
"""

# TODO - To allow cursor to appear on multiple figures, it is necessary to
# connect figure events to callbacks for every existing figure --> do a figure list
# and connect one by one.

# TODO -- move contents of mouse_release etc. to more generic methods

# TODO -- create function draw() which adds points without saving anything

# TODO -- merge key and mouse events management to avoid duplicates


import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import time

# ================================= example ==================================


def main():
    """ Example of use."""
    x = [0, 1, 2, 3, 4]
    y = [4, 7, 11, 18, 33]

    z = np.random.randn(1000)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(x, y, '-ob')
    ax2.plot(z, '-ok')
    
    plt.show()
    
    hinput(4)

    # = Cursor(block=True, record_clicks=True, n=3, show_clicks=True, timeout=2)
    
    #plt.show()

    # fig2, ax3 = plt.subplots()
    # ax3.plot(y, x, '-ok')

    # c2 = Cursor() 
    
    # #plt.show()
    
    # fig3, ax4 = plt.subplots()
    # ax4.plot(1, 1, 'ok')
    # data = ginput(3)
    # plt.close(fig3)
    
    # plt.show(block=False)

# =============================== Cursor class ===============================


class Cursor:
    """ Cursor following the mouse on any axes of a single figure.

    This class creates a cursor that moves along with the mouse. It is drawn
    only within existing axes, but contrary to the matplotlib widget Cursor,
    is not bound to specific axes: moving the mouse over different axes will
    plot the cursor in these other axes. Right now, the cursor is bound to a
    certain figure, however this could be changed easily.

    Cursor style can be modified with the options `color`, `style` and `width`,
    which correspond to matplotlib's color, linestyle and linewidth respectively.
    By default, color is red, style is dotted (:), width is 1.
    
    Cursor apparance can also be changed by specific key strokes:
        - space bar to toggle visibility (on/off)
        - up/down arrows: increase or decrease width (linewidth)
        - left/right arrows: cycle through different cursor colors

    The cursor can also leave marks and/or record click positions if there is 
    a click with a specific button (by default, left mouse button). Clicks can
    be removed with the remove button (by default, right mouse button), and
    stopped with the stop button (by default, middle mouse button).
    
    Addition / removal / stop of clicks are also achieved by key strokes:
        - 'a' for addition (corresponds to left click)
        - 'z' for removal (corresponds to right click)
        - 'enter' for stopping clicks (corresponds to middle click)
        
    Parameters
    ----------
    All parameters optional so that a cursor can be created by `Cursor()`.
    
    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `color` (matplotlib's color, default: red, i.e. 'r').
    - `style` (matplotlib's linestyle, default: dotted ':').
    - `width` (float, default: 1.0). Line width.
    - `blit` (bool, default: True). Blitting for performance.
    - `show_clicks` (bool, default:False). Mark location of clicks.
    - `record_clicks` (bool, default False). Create a list of click positions.
    
    The 3 following parameters can be 1, 2, 3 (left, middle, right mouse btns).
    - `mouse_add` (int, default 1). 
    - `mouse_pop` (int, default 3). Removes most recently added point.
    - `mouse_stop`(int, default 2). Stops click recording. Same as reaching n.
    
    The 3 following parameters are useful for ginput-like functions.
    - `n` (int, default 1000). Cursor deactivates after n clicks.
    - `block` (bool, default False). Block console until nclicks is reached.
    - `timeout` (float, default 0, i.e. infinite) timeout for blocking.
    
    The last 2 parameters customize appearance of click marks when shown.
    - `mark_symbol` (matplolib's symbol, default: '+')
    - `mark_size` (matplotlib's markersize, default 10)
    
    
    Useful class methods
    --------------------
    
    - `erase_marks()`: erase click marks on the plot. 
    - `erase_data()`: reset recorded click data.
    
    The methods `create` and `erase` are used internally within the class and
    are not meant for the user.
    
    Useful class attributes
    -----------------------
    
    - `fig`: matplotlib figure the cursor is active in. Fixed.
    - `ax`: matplotlib axes the cursor is active in. Changes in subplots.
    - `visibility`: bool, sets whether cursor drawn or not when in axes.
    - `inaxes`: book, true when mouse (and thus cursor) is in axes
    - `clicknumber`: track the number of recorded clicks.
    - `clickdata`: stores the (x, y) data of clicks in a list.
    - `marks`: list of matplotlib artists containing all click marks drawn.
        
    Notes
    -----
    
    - As in matplotlib's ginput, `mouse_add`, `mouse_pop` and `mouse_stop`
    have keystroke equivalents, respectively `a`, `z` and `enter`. Only the
    last one is the same as matplotlib's ginput, to avoid interactions with
    other matplotlib's interactive features (e.g. backspace for "back").

    - Currently, the mark color is always the same as the cursor.
    
    - It is not allowed to have more than 1 cursor per figure, to avoid 
    conflics between cursors in blitting mode.

    - Using panning and zooming works with the cursor on; to enable this,
    blitting is temporarily suspended during a click+drag event.

    - As a result, the cursor does not reappear immediately after panning or
    zooming if blitting is activated, but one needs to move the mouse.

    """

    # Define colors the arrows will cycle through
    # (in addition to the one specified by the user)
    colors = ['r', 'b', 'k', 'w']

    # list of Cursor instances
    cursors = []

    def __init__(self, fig=None, color='r', style=':', width=1, blit=True,
                 show_clicks=False, record_clicks=False,
                 mouse_add=1, mouse_pop=3, mouse_stop=2,
                 n=1000, block=False, timeout=0, 
                 mark_symbol='+', mark_size=10):
        """Note: cursor drawn only when the mouse enters axes."""

        self.fig = plt.gcf() if fig is None else fig

        self.cursor = None  # stores horizontal and vertical lines if active
        self.background = None  # this is for blitting
        self.press = False  # active when mouse is currently pressed
        self.just_released = False  # active only right after mouse click released
        self.blit = blit  # blitting allows for fast rendering

        self.color = color
        if color not in Cursor.colors:
            Cursor.colors.append(color)
        # finds at which position the color is in the list
        self.colorindex = Cursor.colors.index(color)

        self.style = style
        self.width = width

        self.visibility = True  # can be True even if cursor not drawn (e.g. because mouse is outside of axes)
        self.inaxes = False  # True when mouse is in axes

        self.markclicks = show_clicks
        self.recordclicks = record_clicks
        
        self.clickbutton = mouse_add
        self.removebutton = mouse_pop
        self.stopbutton = mouse_stop
        
        self.marksymbol = mark_symbol
        self.marksize = mark_size
        self.clickpos = None  # temporarily stores the click position
        self.clicknumber = 0  # tracks the number of clicks with s
        self.n = n  # maximum number of clicks, after which cursor is deactivated
        self.clickdata = []  # stores the (x, y) data of clicks in a list
        self.marks = []  # list containing all artists drawn
        
        # below is to erase previous cursors on the figure -------------------

        # list all cursors on the same figure
        fig_cursors = [c for c in Cursor.cursors if c.fig == self.fig]

        for cursor in fig_cursors:
            i = Cursor.cursors.index(cursor)
            Cursor.cursors.pop(i)
            cursor.disconnect()
            del cursor

        # put new cursor in list
        Cursor.cursors.append(self)
        
        # this seems to be a generic way to bring window to the front
        # but I have not checked with different backends etc.
        plt.get_current_fig_manager().show()
        
        self.connect()     
        
        # the blocking option below needs to be after connect()
        self.block = block
        if self.block is True:
            self.fig.canvas.start_event_loop(timeout=timeout)

    def __repr__(self):

        base_message = f'Cursor on Fig. {self.fig.number}.'

        if self.clickbutton == 1:
            button = "left"
        elif self.clickbutton == 2:
            button = 'middle'
        elif self.clickbutton == 3:
            button = 'right'
        else:
            button = 'unknown'

        if self.markclicks is True:
            add_message = f"Leaves '{self.marksymbol}' marks when {button} mouse button is pressed. "
        else:
            add_message = ''

        if self.recordclicks is True:
            add_message += f'Positions of clicks with the {button} button is recorded in the clickdata attribute.'
        else:
            add_message += f'Positions of clicks not recorded.'

        return base_message + ' ' + add_message

    def __str__(self):
        return f'Cursor on Fig. {self.fig.number}.'

# =========================== main cursor methods ============================

    def create(self, event):
        """Draw a cursor (h+v lines) that stop at the edge of the axes."""
        ax = self.ax

        pos = (event.xdata, event.ydata)
        (x, y) = pos

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # horizontal and vertical cursor lines, the animated option is for blitting
        hline, = ax.plot([xmin, xmax], [y, y], color=self.color,
                         linewidth=self. width, linestyle=self.style,
                         animated=self.blit)
        vline, = ax.plot([x, x], [ymin, ymax], color=self.color,
                         linewidth=self.width, linestyle=self.style,
                         animated=self.blit)

        # because plotting the lines changes the initial xlim, ylim
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        cursor = (hline, vline)
        self.cursor = cursor
        return cursor

    def erase(self):
        """Erase cursor, called e.g. when the mouse exits the axes."""
        (hline, vline) = self.cursor
        hline.remove()
        vline.remove()
        self.fig.canvas.draw()
        self.cursor = None
        return

    def update_position(self, event):
        """Update position of the cursor to follow mouse event."""

        if self.cursor is None:  # no need to update position if cursor not active
            return

        canvas = self.fig.canvas
        hline, vline = self.cursor
        ax = self.ax

        # If the block below is incorporated in on_mouse_release only, it does not
        # work well, because it seems to get the background data before the
        # plot has been updated
        if self.just_released is True:
            if self.blit is True:
                self.background = canvas.copy_from_bbox(self.ax.bbox)
                self.just_released = False

        if self.blit is True:
            # without this line, the graph keeps all successive positions of
            # the cursor on the screen
            canvas.restore_region(self.background)

        # accommodates changes in axes limits while cursor is on
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        x = event.xdata
        y = event.ydata

        hline.set_xdata([xmin, xmax])
        hline.set_ydata([y, y])
        vline.set_xdata([x, x])
        vline.set_ydata([ymin, ymax])

        if self.blit is True:
            ax.draw_artist(hline)
            ax.draw_artist(vline)
            # without this below, the graph is not updated
            canvas.blit(self.ax.bbox)
        else:
            canvas.draw()

    def erase_marks(self):
        """Erase plotted clicks (marks) without removing click data"""
        for mark in self.marks:
            mark.remove()
        self.fig.canvas.draw()

    def erase_data(self):
        """Erase data of recorded clicks"""
        self.clickdata = []


# ============================ callback functions ============================

    # def on_enter_figure(self, event):
    #     """Attribute figure the mouse is on to the cursor"""
    #     print(self.fig)
    #     self.disconnect()
    #     self.fig = event.canvas.figure
    #     self.connect()
    #     print(self.fig)

    def on_enter_axes(self, event):
        """Create a cursor when mouse enters axes."""

        self.ax = event.inaxes

        self.inaxes = True

        if self.visibility is True:
            self.create(event)

        canvas = self.fig.canvas
        canvas.draw()

        if self.blit is True:
            self.background = canvas.copy_from_bbox(self.ax.bbox)

    def on_leave_axes(self, event):
        """Erase cursor when mouse leaves axes."""

        self.inaxes = False

        if self.cursor is not None:
            self.erase()

    def on_motion(self, event):
        """Update position of the cursor when mouse is in motion."""
        if self.cursor is None:
            return  # no active cursor --> do nothing
        if self.press is True:
            return  # to avoid weird interactions with zooming/panning
        self.update_position(event)

    def on_mouse_press(self, event):
        """If mouse is pressed, deactivate cursor temporarily."""
        self.press=True
        self.clickpos = (event.xdata, event.ydata)

    def on_mouse_release(self, event):
        """When releasing click, reactivate cursor and redraw figure.

        This is in order to accommodate potential zooming/panning
        (done later in on_motion function, using the just_released parameter,
        it does not work if done here directly, not completely sure why).
        """
        self.press = False
        self.just_released = True

        # without the line below, blitting mode keeps the cursor at time of
        # the click plotted permanently for some reason.
        canvas = self.fig.canvas
        canvas.draw()

        x, y = (event.xdata, event.ydata)

        # this avoids recording clicks during panning/zooming
        if (x, y) == self.clickpos:

            if event.button == self.clickbutton:

                if self.recordclicks is True:
                    self.clickdata.append((x, y))
                    self.clicknumber += 1

                if self.markclicks is True:
                    mark, = self.ax.plot(x, y, marker=self.marksymbol, color=self.color,
                                  markersize=self.marksize)
                    self.fig.canvas.draw()
                    self.marks.append(mark)

            elif event.button == self.removebutton:

                if self.recordclicks is True:
                    self.clicknumber -= 1
                    self.clickdata.pop(-1)  # remove last element

                if self.markclicks is True:
                    mark = self.marks.pop(-1)
                    mark.remove()
                    self.fig.canvas.draw()

        if self.clicknumber == self.n or event.button == self.stopbutton:
            print('Cursor disconnected (max number of clicks, or stop button pressed).')
            if self.cursor is not None:
                self.erase()
            self.disconnect()
            if self.block is True:
                self.fig.canvas.stop_event_loop()


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
        
        if event.key == " ":  # Space Bar
            if self.visibility is False:
                self.visibility = True
                if self.inaxes is True:
                    self.create(event)
            else:
                self.visibility = False
                if self.inaxes is True:
                    self.erase()

        if event.key == "up":
            self.width += 0.5

        if event.key == "down":
            self.width = self.width-0.5 if self.width>0.5 else 0.5

        if event.key in ['left', 'right']:
            if event.key == "left":
                self.colorindex -= 1
            else:
                self.colorindex += 1
            self.colorindex = self.colorindex % len(Cursor.colors)
            self.color = Cursor.colors[self.colorindex]

        if event.key in ['right', 'left', 'up', 'down']:
            self.erase()  # easy way to not have to update artist
            self.create(event)

# ------------  hack to be able to see the changes directly ------------------
        if event.key in [" ", 'right', 'left', 'up', 'down']:
            self.update_position(event)
        
# ------------------- commands that mimic mouse events -----------------------
        
        x, y = (event.xdata, event.ydata)
        
        if event.key == 'a':

            if self.recordclicks is True:
                self.clickdata.append((x, y))
                self.clicknumber += 1

            if self.markclicks is True:
                mark, = self.ax.plot(x, y, marker=self.marksymbol, color=self.color,
                              markersize=self.marksize)
                self.fig.canvas.draw()
                self.marks.append(mark)

        # I use 'z' here because backspace (as used in ginput) interferes with the interactive "back" option in matplotlib
        elif event.key == 'z':

            if self.recordclicks is True:
                if self.clicknumber == 0:
                    pass
                else:
                    self.clicknumber -= 1
                    self.clickdata.pop(-1)  # remove last element

            if self.markclicks is True:
                if len(self.marks) == 0:
                    pass
                else:
                    mark = self.marks.pop(-1)
                    mark.remove()
                self.fig.canvas.draw()

        if self.clicknumber == self.n or event.key == 'enter':
            print('Cursor disconnected (max number of clicks, or stop button pressed).')
            if self.cursor is not None:
                self.erase()
            self.disconnect()
            if self.block is True:
                self.fig.canvas.stop_event_loop()
                
        if event.key in ['a', 'z', 'enter']:
            self.just_released = True  # hack to prevent display bugs


    def on_close(self, event):
        """Delete cursor if figure is closed"""
        if self.cursor is not None:
            self.erase()
        self.disconnect()
        self.fig.canvas.stop_event_loop()

# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """Connect figure events to callback functions."""
        #self.enterfig_id = self.fig.canvas.mpl_connect('figure_enter_event', self.on_enter_figure)
        self.enterax_id = self.fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.leaveax_id = self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.motion_id = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.pressb_id = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.releaseb_id = self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.pressk_id = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.closefig_id = self.fig.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        """Disconnect figure events from callback functions."""
        #self.fig.canvas.mpl_disconnect(self.enterfig_id)
        self.fig.canvas.mpl_disconnect(self.enterax_id)
        self.fig.canvas.mpl_disconnect(self.leaveax_id)
        self.fig.canvas.mpl_disconnect(self.motion_id)
        self.fig.canvas.mpl_disconnect(self.pressb_id)
        self.fig.canvas.mpl_disconnect(self.releaseb_id)
        self.fig.canvas.mpl_disconnect(self.pressk_id)
        self.fig.canvas.mpl_disconnect(self.closefig_id)


# ========================== ginput-like functions ==========================


def ginput(*args, **kwargs):
    """Identical to matplotlib's ginput, with added cursor for easier clicking.

    Key shortcuts and mouse clicks follow matplotlib's behavior. The Cursor 
    class only acts on the cursor here (appearance, with key Cursor class 
    associated key shortcuts), not on the clicking and data recording which
    follow matplotlib ginput. See matplotlib.pyplot.ginput for help.
    """
    c = Cursor(record_clicks=False, show_clicks=False, block=False) 
    data = plt.ginput(*args, **kwargs)
    del c
    return data


def hinput(n=1, timeout=0, show_clicks=True,
           mouse_add=1, mouse_pop=3, mouse_stop=2,
           blit=True):
    """Similar to ginput, but zooming/panning does not add extra click data.
    
    Here, contrary to ginput, key shortcuts and mouse clicks follow the
    plov Cursor class behavior, in particular the key shortcuts are
    `a`, `z`, `enter` instead of any key, backspace and enter. See 
    Cursor class documentation for more info. All Cursor class interactive
    features are usable.
    
    Parameters
    ----------
    
    Parameters are exactly the same as matplotlib.pyplot.ginput, with only an
    additional one: blit (bool, default True): blitting for performance.
    
    Returns
    -------
    
    List of tuples corresponding to the list of clicked (x, y) coordinates.
    
    """
    c = Cursor(block=True, record_clicks=True, show_clicks=show_clicks, n=n,
               mouse_add=mouse_add, mouse_stop=mouse_stop, mouse_pop=mouse_pop,
               blit=blit)
    data = c.clickdata
    time.sleep(0.2) # just to have time to see the last click and its mark
    c.erase_marks()
    del c
    return data
    

# ================================ direct run ================================

if __name__ == '__main__':
    main()
