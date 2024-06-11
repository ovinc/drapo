"""Extensions to Matplotlib: Line class (draggable line)"""

# TODO -- add double click to "freeze" line to avoid moving it by mistake later?
# TODO -- add more keystroke controls ?
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
    - `verbose` (bool, default False). If True, some events associated with
                interactive objects are printed in the console.
    - `timeout` (float, default 0, i.e. infinite) timeout for blocking.
    """

    name = 'Draggable Line'

    def __init__(
        self,
        ax=None,
        pickersize=5,
        color=None,
        c=None,
        ptstyle='.',
        ptsize=8,
        linestyle='-',
        linewidth=1,
        avoid_existing=True,
        blit=True,
        block=False,
        verbose=False,
        timeout=0,
    ):

        super().__init__(
            ax=ax,
            color=color,
            c=c,
            blit=blit,
            block=block,
            verbose=verbose,
        )

        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()

        self.create(
            pickersize,
            self.color,
            ptstyle,
            ptsize,
            linestyle,
            linewidth,
            avoid_existing,
        )

        # to prevent any shift in axes limits when instanciating line.
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        self.draw_canvas()
        self.update_background()

        if self.block:
            self.fig.canvas.start_event_loop(timeout=timeout)

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
        pt1, = self.ax.plot(x1, y1, marker=ptstyle, color=color, markersize=ptsize)
        pt2, = self.ax.plot(x2, y2, marker=ptstyle, color=color, markersize=ptsize)

        # create connecting line (link) ---------------------------------------
        x1, y1 = self.get_pt_position(pt1, 'data')
        x2, y2 = self.get_pt_position(pt2, 'data')

        link, = self.ax.plot([x1, x2], [y1, y2], c=color,
                             linestyle=linestyle, linewidth=linewidth)

        # assemble lines and pts into "all" ----------------------------------
        self.link = link
        self.all_artists = pt1, pt2, link
        self.all_pts = pt1, pt2

        # make all components of the objects pickable ------------------------
        for artist in self.all_artists:
            artist.set_picker(True)

        # Adjust pick tolerance depending on component -----------------------
        link.set_pickradius(pickersize)
        for pt in self.all_pts:
            pt.set_pickradius(pickersize + ptsize / 2)

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

        if len(self.picked_artists) == 1 and self.link in self.picked_artists:
            # only the line is selected --> move as a whole, make both self.pts active
            active_pts = set(self.all_pts)

        else:
            # in all other cases, the points that need to be active are
            # all the ones picked. If one pt is picked, move only this point
            # and the line (edge mode). If two pts are picked (e.g. because
            # they overlap), move the whole thing as a whole again. If nothing
            # is picked, nothing happens (should not happen because the current
            # method is only called for active objects)
            active_pts = set(self.picked_artists) - {self.link}

        npts = len(active_pts)

        if npts > 1:
            self.active_info = {'mode': 'whole', 'pts': active_pts}
        elif npts == 1:
            self.active_info = {'mode': 'edge', 'pts': active_pts}
        else:
            # Again, this should not happen
            print('Warning: Line.set_active_info() called while no artists '
                  'picked. Please report bug.')

    def update_position(self, event):
        """Update object position depending on moving mode and mouse position."""

        x, y = event.x, event.y  # pixel coordinates

        mode = self.active_info['mode']
        active_pts = self.active_info['pts']

        # EDGE mode: move just one point, the other one stays fixed ----------
        if mode == 'edge':
            pt, = active_pts  # should be the only pt in active_pts
            self.moving_positions[pt] = x, y

        # WHOLE mode: move the line as a whole in a parallel fashion ---------
        else:
            # get where click was initially made and calculate motion
            x0, y0 = self.press_info['click']
            dx, dy = x - x0, y - y0

            for pt in active_pts:
                x0_pt, y0_pt = self.press_info[pt]
                self.moving_positions[pt] = x0_pt + dx, y0_pt + dy

        # now apply the changes to the graph
        for pt in active_pts:
            xnew, ynew = self.pxtodata(self.moving_positions[pt])
            pt.set_data([xnew], [ynew])

        pt1, pt2, link = self.all_artists
        x1, y1 = self.pxtodata(self.moving_positions[pt1])
        x2, y2 = self.pxtodata(self.moving_positions[pt2])
        link.set_data([x1, x2], [y1, y2])

    def get_position(self):
        """Get position ((x1, y1), (x2, y2)) in data coordinates."""
        positions = []

        for pt in self.all_pts:
            position = self.get_pt_position(pt, 'data')
            positions.append(position)

        return tuple(positions)

# ============================= callback methods =============================

    def on_key_press(self, event):
        if event.key == 'enter':
            if self.verbose:
                print('Line position recorded. Line deleted.')
            self.recorded_position = self.get_position()
            self.delete()


# ======================== function rinput ===================================


def linput(**kwargs):
    """Select position information with interactive Line (enter to validate).

    Parameters
    ----------
    Same as drapo.Line(), but block remains always True by default

    Returns
    -------
    Tuple of tuples ((x1, y1), (x2, y2)) of data coordinates (unordered)
    """
    if 'block' in kwargs:
        kwargs.pop('block')

    line = Line(block=True, **kwargs)
    try:
        position = line.recorded_position
    except AttributeError:
        print('Warning - Line deleted before data validation. Returning None.')
        position = None
    return position
