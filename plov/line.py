"""Extensions to Matplotlib: Line class (draggable line)"""

# TODO: -- interactive initiation of line position (with ginput or equivalent)
# TODO: -- add double click to "freeze" line to avoid moving it by mistake later?

# TODO -- be able to continue to drag line even if mouse is outside of axes
# (probably, need to use figure coordinate transforms)

# TODO -- add keystroke controls (e.g. to delete the line)

# TODO -- use pixel coordinates to avoid confusing motion when axes are not
# lineat e.g. logscale.

import matplotlib.pyplot as plt
import numpy as np
import math as m

# ================================= example ==================================

def main():
    """ example of instances of Lines in different figures and axes"""
    fig, ax = plt.subplots()
    ax.plot([1, 0], [11, 13], '-r')

    drag = Line()

    fig2, ax2 = plt.subplots()
    tt = np.linspace(0, 4, 100000)
    xx = np.exp(-tt)
    ax2.plot(tt, xx, '-b')

    drag2 = Line()

    z = np.random.randn(1000)

    fig3, (ax3, ax4) = plt.subplots(1, 2)
    ax3.plot(tt, xx)
    ax4.plot(z, '-ob')

    Line(ax=ax3)
    Line(ax=ax4)

    Line()

    plt.show(block=False)


# ================================ line class ================================


class Line:
    """Interactive draggable line on matplotlib figure/axes.

    The line is composed of three elements : two points at the edge (pt1, pt2)
    and the line between them (link), with customizable appearance.

    Dragging the line can be done in two different ways:
        - clicking on one edge: then the other edge is fixed during motion
        - clicking on the line itself: then the line moves as a whole

    Right-clicking removes and deletes the line.


    Parameters
    ----------
    All parameters optional so that a line can simply be created by `Line()`.

    - `pos` (4-tuple, default: (.2, .2, .8, .8)). Initial position in axes.
    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `ax` (matplotlib axes, default: current axes, specified as None).
    - 'pickersize' (float, default: 5), tolerance for line picking.
    - `color` (matplotlib's color, default: red, i.e. 'r').

    Appearance of the edge points (pt1, pt2):
    - `edgestyle` (matplotlib's marker, default: dot '.').
    - `edgesize` (float, default: 5). Marker size.

    Appearance of the connecting line (link):
    - `linestyle` (matplotlib's linestyle, default: continous '-').
    - `linewidth` (float, default: 1). Line width.
    

    Notes
    -----
    
    - By default, the line is created on the active figure/axes. 
    To instanciate a line in other figure/axes, either specify the key/ax
    parameters, or use `ClickFig()` to activate these axes.
    
    - If the figure uses non-linear axes (e.g. log), dragging the line as a 
    whole can generate confusing motion. It is better to use edge dragging 
    only in this situation. This "bug" could be fixed by tracking pixel 
    motion of the line instead of axes coordinates.

    - For now, control over a line is lost when the mouse exits the axes. If
    this happens, just bring the mouse back in the axes and click on the line.

    - When instanciating a line, there is a check to see if any of the edges
    overlap with an edge of an existing line. If it's the case, the line is
    shited (up and left) to avoid overlapping.

    - If edges of different lines overlap at some point, it is easy to
    separate them by clicking on one of the lines, away from the edges, to
    drag it awway.

    - If two lines coincide completely (within pickersize), it is however not
    possible to separate them again. Best is to consider them as a single line
    and instanciate another line.
    """

    all_lines = []  # list of all instances of lines
    moving_lines = []  # list of lines curently selected for moving
    background = None  # background save for blitting
    expecting_motion = False  # True when the leading line had been selected

    # (leading line is the one that triggers motion of the other selected lines
    # in the case where there are several lines moving at the same time. This
    # feature is for synchronizing issues in blitting mode.

    def __init__(self, pos=(.2, .2, .8, .8), fig=None, ax=None, blit=True,
                 pickersize=5, color='k',
                 edgestyle='.', edgesize=5,
                 linestyle='-', linewidth=1):

        self.fig = plt.gcf() if fig is None else fig
        self.ax = plt.gca() if ax is None else ax

        self.blit = blit
        self.leader = False

        # This is because adding lines can re-dimension axes limits
        self.xlim = self.ax.get_xlim()
        self.ylim = self.ax.get_ylim()

        # set position of line on screen so that it does not overlap others
        x1, y1, x2, y2 = Line.set_position(self, pos, pickersize)

        # create edge points -------------------------------------------------

        pt1, = self.ax.plot(x1, y1, marker=edgestyle, color=color,
                            markersize=edgesize, picker=edgesize)
        pt2, = self.ax.plot(x2, y2, marker=edgestyle, color=color,
                            markersize=edgesize, picker=edgesize)

        self.pt1 = pt1              # first point
        self.pt2 = pt2              # second point

        # create connecting line (link) ---------------------------------------

        x1, y1 = Line.get_pt_position(self.pt1)
        x2, y2 = Line.get_pt_position(self.pt2)

        ax = self.ax

        self.link, = ax.plot([x1, x2], [y1, y2], picker=pickersize,
                             linestyle='-', linewidth=linewidth, color=color)

        # assemble lines and pts into "all" ----------------------------------
        self.all = (self.pt1, self.pt2, self.link)

        # indicates if object moves as a whole ('line') or with just one edge
        # moving ('point'); is None when object not moving
        self.motionmode = None
        # active (moving) points: stores pt1 or pt2 in 'point' mode, stores
        # 'all' in 'line' mode, stores None when not moving
        self.active = None
        self.inactive = 'all'  # inactive points
        # (pt2 or pt1 in 'point' mode, None  in 'line', 'all' when not moving)
        self.press = None  # stores useful buttonpress info

        # set that stores info about what artists of the line are picked
        self.selected = set()

        self.connect()  # connect to fig events

        Line.all_lines.append(self)

        # self.fig.canvas.draw()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        # this seems to be a generic way to bring window to the front but I
        # have not checked with all backends etc, and it does not always work
        plt.get_current_fig_manager().show()

    def __repr__(self):
        drag_figs = [drag.fig for drag in Line.all_lines]
        ndragonfig = drag_figs.count(self.fig)
        return f'Draggable Line #{ndragonfig} on Fig. {self.fig.number} \n'

    def __str__(self):
        return 'Draggable Line on Fig. {self.fig.number}'


# ============================ main line methods =============================


    def set_position(self, position, pickersize):
        """Set position of new line, avoiding existing lines"""
        mindist = 3*pickersize  # min distance between pts to avoid overlapping
        maxloop = 1e3  # maximum number of loops to try to place the new line

        ax = self.ax

        postopx = ax.transData  # transform between data coords to px coords.
        pxtopos = ax.transData.inverted()  # pixels to data coordinates

        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        (a1, b1, a2, b2) = position

        x1, y1 = (1-a1)*xmin + a1*xmax, (1-b1)*ymin + b1*ymax  # default pos.
        x2, y2 = (1-a2)*xmin + a2*xmax, (1-b2)*ymin + b2*ymax

        [X1, Y1] = postopx.transform((x1, y1))
        [X2, Y2] = postopx.transform((x2, y2))

        dragonax = []  # list of coords (px) of existing lines in the current axes

        for drag in Line.all_lines:

            # if on same axis, record coords in a list to check overlap later
            if drag.ax is ax:

                x1b, y1b = Line.get_pt_position(drag.pt1)
                x2b, y2b = Line.get_pt_position(drag.pt2)
                [X1b, Y1b] = postopx.transform((x1b, y1b))
                [X2b, Y2b] = postopx.transform((x2b, y2b))
                dragonax.append((X1b, Y1b))
                dragonax.append((X2b, Y2b))

        for i in range(int(maxloop)):

            for coords in dragonax:

                (Xb, Yb) = coords

                D1 = m.hypot(X1-Xb, Y1-Yb)
                D2 = m.hypot(X2-Xb, Y2-Yb)

                Dmin = min(D1, D2)

                if Dmin < mindist:  # some of the points are too close

                    X1 += -mindist  # shift everything in a parallel manner
                    Y1 += +mindist
                    X2 += -mindist
                    Y2 += +mindist

                    break

            # for / else construction : if the inner for loop finishes, it
            # means all points are ok, so break the main for loop.
            else:
                break

        else:
            print('Warning: Could not find suitable position for new DragLine')

        [x1, y1] = pxtopos.transform((X1, Y1))  # back to data coordinates
        [x2, y2] = pxtopos.transform((X2, Y2))

        return x1, y1, x2, y2

    @staticmethod
    def get_pt_position(pt):
        "Gets point position as a tuple, from line data"
        xpt = pt.get_xdata()
        ypt = pt.get_ydata()

        x = xpt.item()  # convert numpy array to scalar
        y = ypt.item()

        return x, y

    def inactive_select(self):
        """returns inactive artists in the line given the active ones"""
        if self.active == None: return 'all'
        if self.active == 'all': return None
        if self.active == self.pt1: return self.pt2
        if self.active == self.pt2: return self.pt1

    def update_position(self, event):
        """update position of moving artists to follow the mouse"""
        x = event.xdata
        y = event.ydata

        canvas = self.fig.canvas
        ax = self.ax

        if self.blit is True and Line.expecting_motion is True:
            canvas.draw()
            Line.background = canvas.copy_from_bbox(self.ax.bbox)
            Line.expecting_motion = False

        if self.blit is True:
            # without this line, the graph keeps all successive positions of
            # the cursor on the screen
            canvas.restore_region(self.background)

        # now the leader triggers update of all moving artists including itself
        for line in Line.moving_lines:

            # move just one point, the other one stays fixed
            if line.motionmode == 'point':

                x_inact, y_inact = line.inactpos

                line.active.set_xdata(x)  # update position of active point
                line.active.set_ydata(y)

                line.link.set_xdata([x, x_inact])  # update position of line
                line.link.set_ydata([y, y_inact])

            # move the line as a whole in a parallel fashion
            elif line.motionmode == 'line':

                # get where click was initially made
                x1, y1, x2, y2, xpress, ypress = line.press

                dx = x - xpress             # calculate motion
                dy = y - ypress

                line.pt1.set_xdata(x1+dx)
                line.pt1.set_ydata(y1+dy)

                line.pt2.set_xdata(x2+dx)
                line.pt2.set_ydata(y2+dy)

                line.link.set_xdata([x1+dx, x2+dx])
                line.link.set_ydata([y1+dy, y2+dy])

            # Draw all artists of the line (if not, some can miss in motion)
            if self.blit is True:
                ax.draw_artist(line.pt1)
                ax.draw_artist(line.pt2)
                ax.draw_artist(line.link)

        # without this below, the graph is not updated
        if self.blit is True:
            canvas.blit(ax.bbox)
        else:
            canvas.draw()

        return

    def erase(self):

        self.pt1.remove()
        self.pt2.remove()
        self.link.remove()

        self.disconnect()  # useful ?

        Line.all_lines.remove(self)

        del self


# ============================ callback functions ============================


    def on_pick(self, event):
        """If picked, save picked objects, or delete objects if right click"""
        selected = event.artist

        # right click anywhere on the line, including ends, and it removes it.
        if event.mouseevent.button == 3 and (selected is self.link):
            self.erase()
            self.fig.canvas.draw()
            return

        if selected in self.all:
            self.selected.add(selected)

    def on_press(self, event):
        """once the selected points are known, on_press manages how to
        define active and inactive elements
        """

        if len(self.selected) == 0:
            return
        # if any component of the line is selected, it means the line is moving
        else:
            Line.moving_lines.append(self)
            if self.blit is True:
                for artist in self.all:
                    artist.set_animated(True)

        # if several moving lines, save background (for blitting) only once.
        # the line selected first becomes the leader for moving events, i.e.
        # it is the one that detects mouse moving and triggers re-drawing of
        # all other moving lines.
        # Note : all moving lines are necesary on the same axes
        if len(Line.moving_lines) == 1:
            self.leader = True
            # Below is to delay background setting for blitting until all
            # artists have been defined as animated.
            # This is because the canvas.draw() and/or canvas_copy_from_bbox()
            # calls need to be made with all moving artists declared as animated
            Line.expecting_motion = True
            self.fig.canvas.draw()

        if len(self.selected) == 2:  # in this case, one edge has been selected

            self.selected.remove(self.link)  # remove link to have only the pt
            # extract the point, which should be the last element in the set
            selected = self.selected.pop()

            # WARNING: at this stage, self.selected should now be an empty set

            self.active = selected  # selected point becomes active
            self.inactive = self.inactive_select()  # the other one is inactive
            self.inactpos = Line.get_pt_position(self.inactive)

            self.motionmode = 'point'

        # in this case, the "link" has been picked --> line moved as a whole.
        if len(self.selected) == 1:

            x1, y1 = Line.get_pt_position(self.pt1)
            x2, y2 = Line.get_pt_position(self.pt2)

            # store location of pts and of click
            self.press = x1, y1, x2, y2, event.xdata, event.ydata
            self.active = 'all'

            self.motionmode = 'line'

    def on_motion(self, event):

        if self.motionmode==None: return

        # only the leader triggers moving events (others drawn in update_position)
        if self.leader is True:
            self.update_position(event)

    def on_release(self, event):
        """If mouse released, reset all variables related to line moving"""
        if self.active is None:
            return
        else:
            if self.blit is True:
                for artist in self.all:
                    artist.set_animated(False)

        self.motionmode = None
        self.active = None
        self.inactive = 'all'
        self.press = None
        self.selected = set()  # empty set

        # Reset class variable that store moving information
        Line.moving_lines = []
        Line.expecting_motion = False
        Line.background = None

    def on_leave_axes(self, event):
        """If mouse leaves axes it is considered the same as unclicking"""
        self.on_release(event)

    def on_close(self, event):
        "if figure is closed, remove line from the list of lines"
        if self in Line.all_lines:
            Line.all_lines.remove(self)
        self.disconnect()


# ================= connect/disconnect events and callbacks ==================


    def connect(self):
        'connect object to figure canvas events'

        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidpick = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidaxleave = self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.cidclose = self.fig.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        'disconnect callback ids'
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidpick)
        self.fig.canvas.mpl_disconnect(self.cidaxleave)
        self.fig.canvas.mpl_disconnect(self.cidclose)


# ================================ direct run ================================

if __name__ == '__main__':
    main()
