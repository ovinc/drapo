"""Extensions to Matplotlib: Line class (draggable line)"""

# TODO -- add blocking behavior to be able to measure slopes etc.
# TODO -- add double click to "freeze" line to avoid moving it by mistake later?
# TODO -- add keystroke controls (e.g. to delete the line)?
# TODO -- key press to make the line exactly vertical or horiztontal
# TODO -- live indication of the slope of the line.
# TODO -- add a blocking option ?

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math as m

from .interactive_object import InteractiveObject

# ================================= Testing ==================================

def main(blit=True, backend=None):  # For testing purposes
    
    if backend is not None:
        matplotlib.use(backend)
    
    """ example of instances of Lines in different figures and axes"""
    fig1, ax1 = plt.subplots()
    tt = np.linspace(0, 4, 100000)
    xx = np.exp(-tt)
    ax1.plot(tt, xx, '-b')
    
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    l1 = Line()

    z = np.random.randn(1000)

    fig2, (ax2a, ax2b) = plt.subplots(1, 2)
    ax2a.plot(tt, xx)
    ax2b.plot(z, '-ob')
    
    ax2a.set_yscale('log')

    l2 = Line(ax=ax2a)
    l3 = Line(ax=ax2b)

    l4 = Line(blit=blit)  # this one is plot in current axes, and sets the blit behavior of all lines

    plt.show(block=False)
    
    return l1, l2, l3, l4


# ================================ Line class ================================


class Line(InteractiveObject):
    """Interactive draggable line on matplotlib figure/axes.
    
    Left click anywhere on the line to drag it, right click to remove it.

    Parameters
    ----------
    All parameters optional so that a line can simply be created by `Line()`.

    - `pos` (4-tuple, default: (.2, .2, .8, .8)). Initial position in axes.
    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `ax` (matplotlib axes, default: current axes, specified as None).
    - 'pickersize' (float, default: 5), tolerance for line picking.
    - `color` (matplotlib's color, default: None (class default value)).

    Appearance of the edge points:
    - `ptstyle` (matplotlib's marker, default: dot '.').
    - `ptsize` (float, default: 5). Marker size.

    Appearance of the connecting line:
    - `linestyle` (matplotlib's linestyle, default: continuous '-').
    - `linewidth` (float, default: 1). Line width.
    
    Instanciation option:
    - `avoid_existing` (bool, default:True). Avoid overlapping existing lines
    (only avoids that edge points overlap, but lines can still cross).
    
    Other
    - `blit` (bool, default True). If True, blitting is used for fast rendering
    - `block`(bool, default False). If True, object blocks the console
    (block not implemented yet for Line and Rect)
    """
    
    name = 'Draggable Line'
    

    def __init__(self, pos=(.2, .2, .8, .8), fig=None, ax=None,
                 pickersize=5, color=None,
                 ptstyle='.', ptsize=5,
                 linestyle='-', linewidth=1,
                 avoid_existing = True,
                 blit=True, block=False
                 ):
        
        super().__init__(fig=fig, ax=ax, color=color, blit=blit, block=block)

        options = (pos, pickersize, self.color, ptstyle, ptsize, 
                   linestyle, linewidth, avoid_existing)
        # create line, and attributes pt1, pt2, link
        self.create(options)

        # to prevent any shift in axes limits when instanciating line. The
        # initial self.xlim / self.ylim setting is done in InteractiveObject
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        
        self.fig.canvas.draw()


# ============================ main line methods =============================

# these methods are specific to the Line class and are called by the more
# generic callback functions (see below)

    def create(self, options):
        """Create the line and its components (pt1, pt2, link)"""
        
        # If the structure below is changed, verify that subclasses are
        # changed as well
        (pos, pickersize, color, ptstyle, ptsize, 
         linestyle, linewidth, avoid_existing) = options
        
        # set position of line on screen so that it does not overlap others
        pos = self.__class__.set_initial_position(self, pos, pickersize, 
                                                  avoid_existing)
        x1, y1, x2, y2 = pos

        # create edge points -------------------------------------------------

        pt1, = self.ax.plot(x1, y1, marker=ptstyle, color=color,
                            markersize=ptsize, picker=ptsize)
        pt2, = self.ax.plot(x2, y2, marker=ptstyle, color=color,
                            markersize=ptsize, picker=ptsize)


        # create connecting line (link) ---------------------------------------

        x1, y1 = self.get_pt_position(pt1, 'data')
        x2, y2 = self.get_pt_position(pt2, 'data')

        link, = self.ax.plot([x1, x2], [y1, y2], picker=pickersize,
                                  c=color,
                                  linestyle=linestyle, linewidth=linewidth)

        # assemble lines and pts into "all" ----------------------------------
        self.all_artists = pt1, pt2, link
        self.all_pts = pt1, pt2
        

    def set_initial_position(self, position, pickersize, avoid=True):
        """Set position of new line, avoiding existing lines if necessary."""
        
        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        (a1, b1, a2, b2) = position

        x1, y1 = (1-a1)*xmin + a1*xmax, (1-b1)*ymin + b1*ymax  # default pos.
        x2, y2 = (1-a2)*xmin + a2*xmax, (1-b2)*ymin + b2*ymax
        
        if not avoid:
            return x1, y1, x2, y2
                    
        mindist = 3*pickersize  # min distance between pts to avoid overlapping
        maxloop = 1e3  # maximum number of loops to try to place the new line

        X1, Y1 = self.datatopx((x1, y1))
        X2, Y2 = self.datatopx((x2, y2))

        dragonax = []  # list of coords (px) of existing lines in the current axes

        otherlines = set(self.class_objects()) - set([self])
        for line in otherlines:

            # if on same axis, record coords in a list to check overlap later
            if line.ax is self.ax:
                
                pt1, pt2 = line.all_pts
                X1b, Y1b = self.get_pt_position(pt1, 'px')
                X2b, Y2b = self.get_pt_position(pt2, 'px')
                dragonax.append((X1b, Y1b))
                dragonax.append((X2b, Y2b))

        for i in range(int(maxloop)):

            for coords in dragonax:

                Xb, Yb = coords
                D1 = m.hypot(X1-Xb, Y1-Yb)
                D2 = m.hypot(X2-Xb, Y2-Yb)
                Dmin = min(D1, D2)

                if Dmin < mindist:  # some of the points are too close
                    X1 += -mindist  # shift everything in a parallel manner
                    Y1 += +mindist
                    X2 += -mindist
                    Y2 += +mindist
                    break

            else:  # if the inner for loop finishes, it means all points are ok
                break  # --> exit the outside for loop
  
        x1, y1 = self.pxtodata((X1, Y1))  # back to data coordinates
        x2, y2 = self.pxtodata((X2, Y2))

        return x1, y1, x2, y2


    def set_active_info(self):
        """separates points into active/inactive and detects motion mode"""
        line = self.all_artists[2]
        
        # set which points are active and corresponding motion mode ----------
        
        if len(self.picked_artists) == 1:  # only line selected --> move as a whole
            mode = 'whole'
            active_elements = self.all_artists
            
        elif len(self.picked_artists) == 2:  # line and pt selected --> edge mode
            mode = 'edge'
            active_elements = self.picked_artists
            
        else:  # Normally this case shouldn't happen as this method should 
        # be called only for active objects.
            mode = None
            active_pts = None
        
        active_pts = set(active_elements) - {line}
        
        self.active_info = {'active_pts': active_pts, 'mode': mode}
    

    def update_position(self, event):
        """Update object position depending on moving mode and mouse position."""
        
        x = event.x  # for lines, it is preferrable to work with pixel coordinates
        y = event.y  # (to acommodate log scales etc.)
        
        active_pts = self.active_info['active_pts']
        mode = self.active_info['mode']
        
        # move just one point, the other one stays fixed
        if mode == 'edge':
            [pt] = active_pts  # should be the only pt in active_pts
            x_data, y_data = self.pxtodata((x, y))
            self.x_inmotion[pt] = x_data
            self.y_inmotion[pt] = y_data
        
        # move the line as a whole in a parallel fashion
        elif mode == 'whole':
            # get where click was initially made and calculate motion
            x_press, y_press = self.press_info
            dx = x - x_press['click']
            dy = y - y_press['click']
            
            for pt in active_pts:
                x_new = x_press[pt] + dx
                y_new = y_press[pt] + dy
                x_data, y_data = self.pxtodata((x_new, y_new))
                self.x_inmotion[pt] = x_data
                self.y_inmotion[pt] = y_data

        # now apply the changes to the graph
        for pt in active_pts:
            pt.set_xdata(self.x_inmotion[pt])
            pt.set_ydata(self.y_inmotion[pt])
        
        pt1, pt2, link = self.all_artists
        link.set_xdata([self.x_inmotion[pt1], self.x_inmotion[pt2]])
        link.set_ydata([self.y_inmotion[pt1], self.y_inmotion[pt2]])
        

# ============================ callback functions ============================
    
    def on_pick(self, event):
        """If picked, save picked objects, or delete objects if right click"""
        selected = event.artist
        if event.mouseevent.button == 3 and (selected in self.all_artists):
            self.delete()
            return
        if selected in self.all_artists:
            self.picked_artists.add(selected)
            

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
        if self.__class__.leader is self:
            self.update_graph(event)


    def on_mouse_release(self, event):
        """When mouse released, reset attributes to non-moving"""
        if self not in self.__class__.moving_objects:
            return
        else:
            self.reset_after_motion()
            
            
    def on_key_press(self, event):
        pass
        



# ================================ direct run ================================

if __name__ == '__main__':
    main()
