"""Extensions to Matplotlib: Line class (draggable line)"""

# TODO -- add double click to "freeze" line to avoid moving it by mistake later?
# TODO -- add keystroke controls (e.g. to delete the line)?
# TODO -- key press to make the line exactly vertical or horiztontal
# TODO -- live indication of the slope of the line.

import math as m

from .interactive_object import InteractiveObject


class Line(InteractiveObject):
    """Interactive draggable line in matplotlib figure/axes.

    Left click anywhere on the line to drag it, right click to remove it.

    Parameters
    ----------
    All parameters optional so that a line can simply be created by `Line()`.

    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `ax` (matplotlib axes, default: current axes, specified as None).
    - 'pickersize' (float, default: 5), tolerance for line picking.
    - `color` (matplotlib's color, default: None (class default value)).
    - `c` (shortcut for `color`)

    Appearance of the edge points:
    - `ptstyle` (matplotlib's marker, default: dot '.').
    - `ptsize` (float, default: 5). Marker size.

    Appearance of the connecting line:
    - `linestyle` (matplotlib's linestyle, default: continuous '-').
    - `linewidth` (float, default: 1). Line width.

    Instantiation option:
    - `avoid_existing` (bool, default:True). Avoid overlapping existing lines
    (only avoids that edge points overlap, but lines can still cross).

    Other
    - `blit` (bool, default True). If True, blitting is used for fast rendering
    - `block`(bool, default False). If True, object blocks the console
    (block not implemented yet for Line and Rect)
    """

    name = 'Draggable Line'

    def __init__(self, fig=None, ax=None, pickersize=5, color=None, c=None,
                 ptstyle='.', ptsize=5, linestyle='-', linewidth=1,
                 avoid_existing=True, blit=True, block=False):

        super().__init__(fig=fig, ax=ax, color=color, c=c,
                         blit=blit, block=block)

        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()

        self.create(pickersize, self.color, ptstyle, ptsize,
                    linestyle, linewidth, avoid_existing)

        # to prevent any shift in axes limits when instanciating line. The
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        self.fig.canvas.draw()  # Useful?

    # ========================== main line methods ===========================

    # these methods are specific to the Line class and are called by the
    # more generic callback functions defined in InteractiveObject or below

    def create(self, pickersize, color, ptstyle, ptsize, linestyle,
               linewidth, avoid_existing):
        """Create the line and its components (pt1, pt2, link)"""

        # set position of line on screen so that it does not overlap others --
        pos = self.__class__.set_initial_position(self, pickersize, avoid_existing)
        (x1, y1), (x2, y2) = pos

        # create edge points -------------------------------------------------
        pt1, = self.ax.plot(x1, y1, marker=ptstyle, color=color,
                            markersize=ptsize, picker=True, pickradius=ptsize)
        pt2, = self.ax.plot(x2, y2, marker=ptstyle, color=color,
                            markersize=ptsize, picker=True, pickradius=ptsize)

        # create connecting line (link) ---------------------------------------
        x1, y1 = self.get_pt_position(pt1, 'data')
        x2, y2 = self.get_pt_position(pt2, 'data')

        link, = self.ax.plot([x1, x2], [y1, y2], c=color,
                             picker=True, pickradius=pickersize,
                             linestyle=linestyle, linewidth=linewidth)

        # assemble lines and pts into "all" ----------------------------------
        self.all_artists = pt1, pt2, link
        self.all_pts = pt1, pt2

    def set_initial_position(self, pickersize, avoid=True):
        """Set position of new line, avoiding existing lines if necessary."""

        a1, b1, a2, b2 = .2, .2, .8, .8  # relative initial position in axes

        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        # Move into px coordinates to avoid problems with nonlinear axes
        xmin, ymin = self.datatopx((xmin, ymin))
        xmax, ymax = self.datatopx((xmax, ymax))

        # default positions
        x1, y1 = (1 - a1) * xmin + a1 * xmax, (1 - b1) * ymin + b1 * ymax
        x2, y2 = (1 - a2) * xmin + a2 * xmax, (1 - b2) * ymin + b2 * ymax

        if avoid:
            mindist = 3 * pickersize  # min distance between pts to avoid overlapping
            dragonax = []  # list of coords (px) of existing lines in the current axes

            otherlines = set(self.class_objects()) - set([self])
            for line in otherlines:
                # if on same axis, record coords in a list to check overlap later
                if line.ax is self.ax:
                    pt1, pt2 = line.all_pts
                    x1b, y1b = self.get_pt_position(pt1, 'px')
                    x2b, y2b = self.get_pt_position(pt2, 'px')
                    dragonax.append((x1b, y1b))
                    dragonax.append((x2b, y2b))

            while True:
                for (xb, yb) in dragonax:
                    d1 = m.hypot(x1 - xb, y1 - yb)
                    d2 = m.hypot(x2 - xb, y2 - yb)
                    dmin = min(d1, d2)
                    if dmin < mindist:  # some of the points are too close
                        x1 += -mindist  # shift everything in a parallel manner
                        y1 += +mindist
                        x2 += -mindist
                        y2 += +mindist
                        break
                else:  # if the inner for loop finishes, it means all points are ok
                    break  # --> exit the outside while loop

        return self.pxtodata((x1, y1)), self.pxtodata((x2, y2))

    def set_active_info(self):
        """Set active/inactive points during motion and detect motion mode."""
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

        x, y = event.x, event.y  # pixel coordinates

        active_pts = self.active_info['active_pts']
        mode = self.active_info['mode']

        # move just one point, the other one stays fixed
        if mode == 'edge':
            [pt] = active_pts  # should be the only pt in active_pts
            self.moving_positions[pt] = x, y

        # move the line as a whole in a parallel fashion
        elif mode == 'whole':
            # get where click was initially made and calculate motion
            x0, y0 = self.press_info['click']
            dx, dy = x - x0, y - y0

            for pt in active_pts:
                x0_pt, y0_pt = self.press_info[pt]
                self.moving_positions[pt] = x0_pt + dx, y0_pt + dy

        # now apply the changes to the graph
        for pt in active_pts:
            xnew, ynew = self.pxtodata(self.moving_positions[pt])
            pt.set_data(xnew, ynew)

        pt1, pt2, link = self.all_artists
        x1, y1 = self.pxtodata(self.moving_positions[pt1])
        x2, y2 = self.pxtodata(self.moving_positions[pt2])
        link.set_data([x1, x2], [y1, y2])

# ============================= callback methods =============================

    def on_key_press(self, event):
        pass
