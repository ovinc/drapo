"""Extensions to Matplotlib: Line class (draggable line)"""

# TODO: -- interactive initiation of line position (with ginput or equivalent)
# TODO: -- add double click to "freeze" line to avoid moving it by mistake later?

# TODO -- be able to continue to drag line even if mouse is outside of axes
# (probably, need to use figure coordinate transforms)

# TODO -- add keystroke controls (e.g. to delete the line)

# TODO -- use pixel coordinates to avoid confusing motion when axes are not
# linear e.g. logscale.

import matplotlib.pyplot as plt
import numpy as np
import math as m

from .interactive_object import InteractiveObject

# ================================= example ==================================

def main():
    """ example of instances of Lines in different figures and axes"""
    fig, ax = plt.subplots()
    ax.plot([1, 0], [11, 13], '-r')

    l1 = Line()

    fig2, ax2 = plt.subplots()
    tt = np.linspace(0, 4, 100000)
    xx = np.exp(-tt)
    ax2.plot(tt, xx, '-b')

    l2 = Line()

    z = np.random.randn(1000)

    fig3, (ax3, ax4) = plt.subplots(1, 2)
    ax3.plot(tt, xx)
    ax4.plot(z, '-ob')

    Line(ax=ax3)
    Line(ax=ax4)

    l3 = Line()

    plt.show(block=False)
    
    return l1, l2, l3


# ================================ line class ================================


class Line(InteractiveObject):
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
    - `color` (matplotlib's color, default: None (class default value)).

    Appearance of the edge points (pt1, pt2):
    - `ptstyle` (matplotlib's marker, default: dot '.').
    - `ptsize` (float, default: 5). Marker size.

    Appearance of the connecting line (link):
    - `linestyle` (matplotlib's linestyle, default: continous '-').
    - `linewidth` (float, default: 1). Line width.
    
    Instanciation option:
    - `avoid_existing` (bool, default:True). Avoid overlapping existing lines
    (only avoids that edge points overlap, but lines can still cross).
    

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
    
    - The last Line instance dictates the blitting behavior for all existing
    lines (blit=True or blit=False).
    """
    
    name = 'Draggable Line'
    

    def __init__(self, pos=(.2, .2, .8, .8), fig=None, ax=None, blit=True,
                 pickersize=5, color=None,
                 ptstyle='.', ptsize=5,
                 linestyle='-', linewidth=1,
                 avoid_existing = True
                 ):
        
        super().__init__(fig, ax, color)    

        options = (pos, pickersize, self.color, ptstyle, ptsize, 
                   linestyle, linewidth, avoid_existing)
        # create line, and attributes pt1, pt2, link, all
        self.create(options)

        # the last object to be instanciated dictates if blitting is true or not
        self.__class__.blit = blit

        # indicates if object moves as a whole ('line') or with just one edge
        # moving ('point'); is None when object not moving
        self.motionmode = None
        # active (moving) points: stores pt1 or pt2 in 'point' mode, stores
        # 'all' in 'line' mode, stores None when not moving
        self.active_pt = None
        self.inactive_pt = 'all'  # inactive points
        # (pt2 or pt1 in 'point' mode, None  in 'line', 'all' when not moving)
        self.press_info = None  # stores useful buttonpress info

        # set that stores info about what artists are picked
        self.picked_artists = set()

        self.connect()  # connect to fig events

        # to prevent any shift in axes limits when instanciating lins
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)



# ============================ main line methods =============================


    def create(self, options):
        """Creates the line and its components (pt1, pt2, link)"""
        
        (pos, pickersize, color, ptstyle, ptsize, 
         linestyle, linewidth, avoid_existing) = options
        
        # set position of line on screen so that it does not overlap others
        x1, y1, x2, y2 = self.__class__.set_position(self, pos, pickersize, avoid_existing)

        # create edge points -------------------------------------------------

        pt1, = self.ax.plot(x1, y1, marker=ptstyle, color=color,
                            markersize=ptsize, picker=ptsize)
        pt2, = self.ax.plot(x2, y2, marker=ptstyle, color=color,
                            markersize=ptsize, picker=ptsize)

        self.pt1 = pt1              # first point
        self.pt2 = pt2              # second point

        # create connecting line (link) ---------------------------------------


        x1, y1 = self.__class__.get_pt_position(pt1)
        x2, y2 = self.__class__.get_pt_position(pt2)

        self.link, = self.ax.plot([x1, x2], [y1, y2], picker=pickersize,
                                  c=color,
                                  linestyle=linestyle, linewidth=linewidth)

        # assemble lines and pts into "all" ----------------------------------
        self.all_artists = (self.pt1, self.pt2, self.link)
        

    def set_position(self, position, pickersize, avoid=True):
        """Set position of new line, avoiding existing lines if necessary."""
        
        ax = self.ax
        
        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        (a1, b1, a2, b2) = position

        x1, y1 = (1-a1)*xmin + a1*xmax, (1-b1)*ymin + b1*ymax  # default pos.
        x2, y2 = (1-a2)*xmin + a2*xmax, (1-b2)*ymin + b2*ymax
        
        if avoid == False:
            return x1, y1, x2, y2
                    
        mindist = 3*pickersize  # min distance between pts to avoid overlapping
        maxloop = 1e3  # maximum number of loops to try to place the new line

        postopx = ax.transData  # transform between data coords to px coords.
        pxtopos = ax.transData.inverted()  # pixels to data coordinates     

        [X1, Y1] = postopx.transform((x1, y1))
        [X2, Y2] = postopx.transform((x2, y2))

        dragonax = []  # list of coords (px) of existing lines in the current axes

        otherlines = self.all_objects - set([self])
        for line in otherlines:

            # if on same axis, record coords in a list to check overlap later
            if line.ax is ax:

                x1b, y1b = self.__class__.get_pt_position(line.pt1)
                x2b, y2b = self.__class__.get_pt_position(line.pt2)
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
            # This situation actually never happens because instanciation
            # automatically pushes draglines further away, to infinity
            print('Warning: Could not find suitable position for new DragLine')

        [x1, y1] = pxtopos.transform((X1, Y1))  # back to data coordinates
        [x2, y2] = pxtopos.transform((X2, Y2))

        return x1, y1, x2, y2


    def inactive_select(self):
        """returns inactive artists in the line given the active ones"""
        if self.active_pt == None: return 'all'
        if self.active_pt == 'all': return None
        if self.active_pt == self.pt1: return self.pt2
        if self.active_pt == self.pt2: return self.pt1
    

    def update_position(self, position, mode):
        """Update object position depending on moving mode and mouse position."""
        
        x, y = position
        
        # move just one point, the other one stays fixed
        if mode == 'point':

            x_inact, y_inact = self.inactpos

            self.active_pt.set_xdata(x)  # update position of active point
            self.active_pt.set_ydata(y)

            self.link.set_xdata([x, x_inact])  # update position of line
            self.link.set_ydata([y, y_inact])

        # move the line as a whole in a parallel fashion
        elif mode == 'line':

            # get where click was initially made
            x1, y1, x2, y2, xpress, ypress = self.press_info

            dx = x - xpress             # calculate motion
            dy = y - ypress

            self.pt1.set_xdata(x1+dx)
            self.pt1.set_ydata(y1+dy)

            self.pt2.set_xdata(x2+dx)
            self.pt2.set_ydata(y2+dy)

            self.link.set_xdata([x1+dx, x2+dx])
            self.link.set_ydata([y1+dy, y2+dy])
            

    def erase(self):

        self.pt1.remove()
        self.pt2.remove()
        self.link.remove()

        self.disconnect()  # useful ?

        self.__class__.all_objects.remove(self)

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

        if selected in self.all_artists:
            self.picked_artists.add(selected)  # this stores the artists, not the line_objects

    def on_mouse_press(self, event):
        """once the selected points are known, on_mouse_press manages how to
        define active and inactive elements
        """
        if len(self.picked_artists) == 0:
            return
        # if any component of the line is selected, it means the line is moving
        else:
            self.__class__.moving_objects.append(self)
            if self.__class__.blit is True:
                for artist in self.all_artists:
                    artist.set_animated(True)

        # if several moving lines, save background (for blitting) only once.
        # the line selected first becomes the leader for moving events, i.e.
        # it is the one that detects mouse moving and triggers re-drawing of
        # all other moving lines.
        # Note : all moving lines are necesary on the same axes
        if len(self.__class__.moving_objects) == 1:
            self.__class__.leader = self
            # Below is to delay background setting for blitting until all
            # artists have been defined as animated.
            # This is because the canvas.draw() and/or canvas_copy_from_bbox()
            # calls need to be made with all moving artists declared as animated
            self.__class__.expecting_motion = True
            self.fig.canvas.draw()

        if len(self.picked_artists) == 2:  # in this case, one edge has been selected

            self.picked_artists.remove(self.link)  # remove link to have only the pt
            # extract the point, which should be the last element in the set
            selected = self.picked_artists.pop()

            # WARNING: at this stage, self.picked_artists should now be an empty set

            self.active_pt = selected  # selected point becomes active
            self.inactive_pt = self.inactive_select()  # the other one is inactive
            self.inactpos = self.__class__.get_pt_position(self.inactive_pt)

            self.motionmode = 'point'

        # in this case, the "link" has been picked --> line moved as a whole.
        if len(self.picked_artists) == 1:

            x1, y1 = self.get_pt_position(self.pt1)
            x2, y2 = self.get_pt_position(self.pt2)

            # store location of pts and of click
            self.press_info = x1, y1, x2, y2, event.xdata, event.ydata
            self.active_pt = 'all'

            self.motionmode = 'line'

    def on_motion(self, event):

        if self.motionmode==None: return

        # only the leader triggers moving events (others drawn in update_graph)
        if self.__class__.leader is self:
            self.update_graph(event)

    def on_mouse_release(self, event):
        """If mouse released, reset all variables related to line moving"""
        
        if self not in self.__class__.moving_objects:
            return
        else:
            if self.__class__.blit is True:
                for artist in self.all_artists:
                    artist.set_animated(False)
                    
        self.fig.canvas.draw()

        self.motionmode = None
        self.active_pt = None
        self.inactive_pt = 'all'
        self.press_info = None
        self.picked_artists = set()  # empty set

        # Reset class variable that store moving information
        self.__class__.moving_objects = []
        self.__class__.expecting_motion = False
        self.__class__.background = None

    def on_leave_axes(self, event):
        """If mouse leaves axes it is considered the same as unclicking"""
        self.on_mouse_release(event)

    def on_close(self, event):
        "if figure is closed, remove line from the list of lines"
        if self in self.__class__.all_objects:
            self.__class__.all_objects.remove(self)
        self.disconnect()



# ================================ direct run ================================

if __name__ == '__main__':
    main()
