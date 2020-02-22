""" Extensions to Matplotlib: Cursor class, and ginput function.

This module contains a Cursor class (cursor that moves with the mouse) and
a ginput function identical to the matplotlib ginput, but with a cursor.
"""

# TO DO -- add function that returns click position


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

    a = ginput(3)
    print(a)

    #b = Cursor() # this does not seem to work while in main(), but works from console

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
    
    Interactive Key shortcuts:
        - space bar: toggle cursor visitbility (on/off)
        - up/down arrows: increase or decrease size (linewidth)
        - left/right arrows: cycle through different cursor colors

    Using panning and zooming works with the cursor on; to enable this,
    blitting is temporarily suspended during a click+drag event.

    A small bug is that if I create one or several cursors within main()
    they do not show up. Typing Cursor() in the console works, though.
    """
    
    # Define colors the arrows will cycle through
    # (in addition to the one specified by the user)
    colors = ['r', 'b', 'k', 'w']

    def __init__(self, figure=None, color='r', style=':', blit=True, size=1):
        """Note: cursor drawn only when the mouse enters some axes."""
        self.ffg = plt.gcf() if figure is None else figure
        self.cursor = None
        self.background = None  # this is for blitting
        self.press = False
        self.just_released = False
        self.blit = blit
        
        self.color = color
        if color not in Cursor.colors:
            Cursor.colors.append(color)
        # finds at which position the color is in the list
        self.colorindex = Cursor.colors.index(color)

        self.style = style
        self.size = size
        self.visibility = True
        self.connect()
        plt.show()
        
    def __repr__(self):
        return f'Cursor on Fig. {self.ffg.number}.'

    def __str__(self):
        return f'Cursor on Fig. {self.ffg.number}.'
        
# =========================== main cursor methods ============================

    def create(self, event):
        """Draw a cursor (h+v lines) that stop at the edge of the axes."""
        ax = self.aax

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
        self.ffg.canvas.draw()
        self.cursor = None
        return
    
    def delete(self):
        """Delete cursor by erasing its lines and disconnecting callbacks."""
        if self.cursor is not None:
            self.erase()
        self.disconnect()
    
    def update_position(self, event):
        """Update position of the cursor to follow mouse event."""
        hline, vline = self.cursor
        ax = self.aax

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

# ============================ callback functions ============================

    def on_enter_axes(self, event):
        """Create a cursor when mouse enters axes."""
        ax = event.inaxes
        self.aax = ax

        if self.visibility is True:
            self.create(event)

        canvas = self.ffg.canvas
        canvas.draw()

        if self.blit is True:
            self.background = canvas.copy_from_bbox(self.aax.bbox)

    def on_leave_axes(self, event):
        """Erase cursor when mouse leaves axes."""
        if self.cursor is not None:
            self.erase()

    def on_motion(self, event):
        """Update position of the cursor when mouse is in motion."""
        if self.cursor is None: return  # no active cursor --> do nothing
        if self.press is True: return  # to avoid weird interactions with zooming/panning

        canvas = self.ffg.canvas

        # If the block below is incorporated in on_mouse_release only, it does not
        # work well, because it seems to get the backgorund data before the
        # plot has been updated
        if self.just_released is True:
            if self.blit is True:
                self.background = canvas.copy_from_bbox(self.aax.bbox)
                self.just_released = False

        if self.blit is True:
            # without this line, the graph keeps all successive positions of
            # the cursor on the screen
            canvas.restore_region(self.background)
        
        # In this function, only the cursor lines are re-plotted
        self.update_position(event)
    
        if self.blit is True:
            # without this, the graph is not updated
            canvas.blit(self.aax.bbox)
        else:
            canvas.draw()

    def on_mouse_press(self, event):
        """If mouse is pressed, deactivate cursor temporarily."""
        self.press=True

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
        canvas = self.ffg.canvas        
        canvas.draw()
        
        
    def on_key_press(self, event):
        """Key press controls. Space bar toggles cursor visibility.
        
        All controls:
            - space bar: toggles cursor visibility
            - up/down arrows: increase or decrease cursor size
            - left/right arrows: cycles through colors
        """
        if event.key == " ":
            if self.visibility is False:
                self.create(event)
                self.visibility = True
            else:
                self.erase()
                self.visibility = False
                
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
        self.on_motion(event)

    def on_close(self, event):
        """Delete cursor if figure is closed"""
        self.delete()


# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """Connect figure events to callback functions."""
        self.enterax_id = self.ffg.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.leaveax_id = self.ffg.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.motion_id = self.ffg.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.pressb_id = self.ffg.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.releaseb_id = self.ffg.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.pressk_id = self.ffg.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.closefig_id = self.ffg.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        """Disconnect figure events from callback functions."""
        self.ffg.canvas.mpl_disconnect(self.enterax_id)
        self.ffg.canvas.mpl_disconnect(self.leaveax_id)
        self.ffg.canvas.mpl_disconnect(self.motion_id)
        self.ffg.canvas.mpl_disconnect(self.pressb_id)
        self.ffg.canvas.mpl_disconnect(self.releaseb_id)
        self.ffg.canvas.mpl_disconnect(self.closefig_id)
        
        
# ============================= ginput function ==============================

def ginput(*args, **kwargs):
    """Extension of matplotlib's ginput to include a cursor."""
    C = Cursor()            # create cursor
    result = plt.ginput(*args, **kwargs)
    C.delete()
    del C
    return result


# ================================ direct run ================================

if __name__ == '__main__':
    main()
