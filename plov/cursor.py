""" Moving cursor that follows the mouse on a matplotlib figure. Useful to
enhance things like ginput
 """

# TO DO -- add function that returns click position
# TO DO -- add color and style options
# TO DO -- add str and repr


import matplotlib.pyplot as plt
import numpy as np

# ================================= example ==================================


def main():

    x = [0, 1, 2, 3, 4]
    y = [4, 7, 11, 18, 33]

    z = np.random.randn(1000)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(x, y, '-ok')
    ax2.plot(z, '-ob')

    plt.show()
    
    a = ginput(3, show_clicks=True)
    print(a)

# =============================== cursor class ===============================


class Cursor:

    def __init__(self, figure=None):
        self.ffg = plt.gcf() if figure is None else figure
        self.cursor = None
        self.connect()

    def create_cursor(self, position):
        """ creates a cursor in the form of a vertical and horizontal line,
        which stop at the edge of the axes"""
        ax = self.aax
        (x, y) = position
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        hline, = ax.plot([xmin, xmax], [y, y], ':r')  # horizontal cursor line
        vline, = ax.plot([x, x], [ymin, ymax], ':r')  # vertical cursor line

        # because plotting the lines changes the initial xlim, ylim
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        cursor = (hline, vline)
        self.cursor = cursor
        return cursor

    def leave_axes(self, event):
        self.delete_cursor()

    def delete_cursor(self):
        """ deletes cursor, this is called when the mouse exit the axes
        """
        (hline, vline) = self.cursor
        hline.remove()
        vline.remove()
        self.ffg.canvas.draw()
        self.cursor = None
        return

    def connect(self):
        """ connects figure events to callback functions
        """
        self.enterax = self.ffg.canvas.mpl_connect('axes_enter_event', self.enter_axes)
        self.leaveax = self.ffg.canvas.mpl_connect('axes_leave_event', self.leave_axes)
        self.motion = self.ffg.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.pressb = self.ffg.canvas.mpl_connect('button_press_event', self.on_press)
        self.closefig = self.ffg.canvas.mpl_connect('close_event', self.on_close)

    def enter_axes(self, event):
        """ when mouse enters axes, create a cursor
        """
        ax = event.inaxes
        self.aax = ax

        pos = (event.xdata, event.ydata)
        hline, vline = self.create_cursor(pos)

        self.ffg.canvas.draw()

    def on_motion(self, event):
        """ when mouse is in motion, update the position of the cursor
        """
        if self.cursor is None: return  # no active cursor --> do nothing

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

        self.ffg.canvas.draw()

    def on_press(self, event):
        pass
        #print(event)

    def on_close(self, event):
        self.disconnect_cursor()
        
    def disconnect_cursor(self):
        self.ffg.canvas.mpl_disconnect(self.enterax)
        self.ffg.canvas.mpl_disconnect(self.leaveax)
        self.ffg.canvas.mpl_disconnect(self.motion)
        self.ffg.canvas.mpl_disconnect(self.pressb)
        self.ffg.canvas.mpl_disconnect(self.closefig)


def ginput(*args, **kwargs):
    """Extension of matplotlib's ginput to include a cursor"""
    C = Cursor()            # create cursor
    result = plt.ginput(*args, **kwargs)
    C.delete_cursor()
    C.disconnect_cursor()
    del C
    
    return result


# ================================ direct run ================================


if __name__ == '__main__':
    main()
