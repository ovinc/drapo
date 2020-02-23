""" Extensions to Matplotlib: Cursor class, and ginput function.

This module contains a Cursor class (cursor that moves with the mouse) and
a ginput function identical to the matplotlib ginput, but with a cursor.
"""

# TO DO -- use disconnect rather than erase? Same for visibility.
# TO DO -- check cursor with several figures.
# TO DO -- disconnect previous cursor from figure if another one is added.
# TO DO -- allow cursor to go to another figure
# TO DO -- Press enter to clear points

import matplotlib.pyplot as plt
import numpy as np

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

    b = Cursor() # this does not seem to work while in main(), but works from console
    plt.ginput(2)

# =============================== Cursor class ===============================


class Cursor:
    """ Cursor following the mouse on any axes of a single figure.
    
    This class creates a cursor that moves along with the mouse. It is drawn
    only within existing axes, but contrary to the matplotlib widget Cursor,
    is not bound to specific axes: moving the mouse over different axes will
    plot the cursor in these other axes. Right now, the cursor is bound to a
    certain figure, however this could be changed easily.

    Blitting enables smooth motion of the cursor (high fps), but can be
    deactivated with the option blit=False (by default, blit=True).

    Cursor style can be modified with the options color, style and size, which
    correspond to matplotlib's color, linestyle and linewidth respectively.
    By default, color is red, style is dotted (:), size is 1.
    
    The cursor can leave marks and/or record click positions if there is a 
    click with a specific button (by default, left mouse button). Clicks can
    be cancelled with the remove button (by default, right mouse button).
    Options:
        - mark_clicks (bool, False by default)
        - record_clicks (bool, if True, create a list of click positions)
        - click_button (1, 2, or 3 for left, middle, right mouse btn, default 1)
        - remove_button (1, 2 or 3, default is 3, right click)
        - nclicks : cursor is deactivated after nclicks clicks (useful for ginput)
        - mark_symbol (usual matplolib's symbols, default is '+')
        - mark_size (matplotlib's markersize)
        
    Note: currently, the mark color is always the same as the cursor.
    
    The marked clicks associated with a cursor can be removed with 
    `Cursor.erase_marks()`
    and the stored click data can be reset using
    `Cursor.erase_data()`.
    
    Interactive Key shortcuts:
        - space bar: toggle cursor visitbility (on/off)
        - up/down arrows: increase or decrease size (linewidth)
        - left/right arrows: cycle through different cursor colors

    Using panning and zooming works with the cursor on; to enable this,
    blitting is temporarily suspended during a click+drag event.

    A small bug is that if I create one or several cursors within main()
    they do not show up. Typing Cursor() in the console works, though.
    
    Another "bug" is that the cursor does not reappear immediately after
    panning/zooming if blitting is activated, but needs the mouse to move.
    """
    
    # Define colors the arrows will cycle through
    # (in addition to the one specified by the user)
    colors = ['r', 'b', 'k', 'w']

    def __init__(self, fig=None, color='r', style=':', blit=True, size=1, 
                 mark_clicks=False, record_clicks=False,
                 click_button=1, remove_button=3, nclicks=1000,
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
        self.size = size
        
        self.visibility = True  # can be True even if cursor not drawn (e.g. because mouse is outside of axes)
        self.inaxes = False  # True when mouse is in axes
        
        self.markclicks = mark_clicks
        self.recordclicks = record_clicks
        self.clickbutton = click_button
        self.removebutton = remove_button
        self.marksymbol = mark_symbol
        self.marksize = mark_size
        self.clickpos = None  # temporarily stores the click position
        self.clicknumber = 0  # tracks the number of clicks with s
        self.nclicks = nclicks  # maximum number of clicks, after which cursor is deactivated
        self.clickdata = []  # stores the (x, y) data of clicks in a list
        self.marks = []  # list containing all artists drawn
        
        self.connect()
        
        self.fig.canvas.draw()
        
        plt.show()
        
        print("Cursor Initiated")
        
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
                         linewidth=self. size, linestyle=self.style,
                         animated=self.blit)
        vline, = ax.plot([x, x], [ymin, ymax], color=self.color,
                         linewidth=self.size, linestyle=self.style,
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
        
        
        if (x, y) == self.clickpos:  # this avoids recording clicks during panning/zooming
            
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
        
        if self.clicknumber == self.nclicks:
            print('Maximum number of clicks reached. Cursor removed.')
            if self.cursor is not None:
                self.erase()
            self.disconnect()
                   
        
    def on_key_press(self, event):
        """Key press controls. Space bar toggles cursor visibility.
        
        All controls:
            - space bar: toggles cursor visibility
            - up/down arrows: increase or decrease cursor size
            - left/right arrows: cycles through colors
        """
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
            self.size += 0.5
            
        if event.key == "down":
            self.size = self.size-0.5 if self.size>0.5 else 0.5
         
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
            
        # the line below is a hack to be able to see the changes directly
        self.update_position(event)

    def on_close(self, event):
        """Delete cursor if figure is closed"""
        if self.cursor is not None:
            self.erase()
        self.disconnect()


# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """Connect figure events to callback functions."""
        self.enterax_id = self.fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.leaveax_id = self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.motion_id = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.pressb_id = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.releaseb_id = self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.pressk_id = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.closefig_id = self.fig.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        """Disconnect figure events from callback functions."""
        self.fig.canvas.mpl_disconnect(self.enterax_id)
        self.fig.canvas.mpl_disconnect(self.leaveax_id)
        self.fig.canvas.mpl_disconnect(self.motion_id)
        self.fig.canvas.mpl_disconnect(self.pressb_id)
        self.fig.canvas.mpl_disconnect(self.releaseb_id)
        self.fig.canvas.mpl_disconnect(self.pressk_id)
        self.fig.canvas.mpl_disconnect(self.closefig_id)
   
    
# ============================= ginput function ==============================
   
def ginput(*args, **kwargs):
    """Similar to matplotlib's ginput, but with cursor and zoom/pan enabled."""
    C = Cursor()            # create cursor
    plt.ginput(*args, **kwargs)
    del C
    return       

# ================================ direct run ================================

if __name__ == '__main__':
    main()
