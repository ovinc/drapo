"""Interactive, draggable rectangle on matplotlib figure."""


# TODO -- Add option for appearance of center
# TODO -- add possibility to interactively change color


from .interactive_object import InteractiveObject


class Rect(InteractiveObject):
    """Interactive draggable rectangle in matplotlib figure/axes.

    Left click to drag rectangle, right click to remove it. Clicking can be
    done on the edges, vertices (corners), or on the center. These clicks
    trigger different modes of motion.

    Parameters
    ----------
    All parameters optional so that a rectangle can be created by `Rect()`.

    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `ax` (matplotlib axes, default: current axes, specified as None).
    - `position` (4-tuple (xmin, ymin, width, height) in data coordinates;
                  default None, i.e. rectangle automatically centered in axes).
    - 'pickersize' (float, default: 5), tolerance for object picking.
    - `color` (matplotlib's color, default: None (class default value)).
    - `c` (shortcut for `color`)

    Appearance of the vertices (corners):
    - `ptstyle` (matplotlib's marker, default: dot '.').
    - `ptsize` (float, default: 5). Marker size.

    Appearance of the edges (lines):
    - `linestyle` (matplotlib's linestyle, default: continuous '-').
    - `linewidth` (float, default: 1). Line width.

    Other
    - `blit` (bool, default True). If True, blitting is used for fast rendering
    - `block`(bool, default False). If True, object blocks the console
    (block not implemented yet for Line and Rect).
    - `timeout` (float, default 0, i.e. infinite) timeout for blocking.
    """

    name = "Draggable Rectangle"

    def __init__(self, fig=None, ax=None, position=None, pickersize=5, c=None,
                 color=None, ptstyle='.', ptsize=5, linestyle='-', linewidth=1,
                 blit=True, block=False, timeout=0):

        super().__init__(fig=fig, ax=ax, color=color, c=c,
                         blit=blit, block=block)

        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()

        self.create(pickersize, position,
                    ptstyle, ptsize, linestyle, linewidth)

        # to prevent any shift in axes limits when instanciating line. The
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        self.fig.canvas.draw()  # Useful?

        if self.block:
            self.fig.canvas.start_event_loop(timeout=timeout)

    def create(self, pickersize, position,
               ptstyle, ptsize, linestyle, linewidth):

        positions = self.set_initial_position(position)
        corner_positions = positions[:-1]  # the last one is the center

        # Create all vertices (corners) of the rectangle ---------------------
        corners = []
        for pos in corner_positions:
            pt, = self.ax.plot(*pos, marker=ptstyle, c=self.color, picker=True,
                               pickradius=pickersize, markersize=ptsize)
            corners.append(pt)

        # Create all lines (edges) of the rectangle --------------------------
        lines = []
        for i, pos in enumerate(corner_positions):
            x1, y1 = corner_positions[i - 1]
            x2, y2 = pos
            line, = self.ax.plot([x1, x2], [y1, y2], c=self.color,
                                 picker=True, pickradius=pickersize,
                                 linestyle=linestyle, linewidth=linewidth)
            lines.append(line)

        # Create center of rectangle -----------------------------------------
        x_center, y_center = positions[-1]
        center, = self.ax.plot(x_center, y_center, marker='+', c=self.color,
                               markersize=10, picker=True, pickradius=pickersize)

        self.all_artists = (*corners, *lines, center)
        self.all_pts = (*corners, center)

    def set_initial_position(self, position):
        """Set position of new line, avoiding existing lines if necessary.

        Note: this is how the corners and lines are listed:

                          line 3
        corner 3   ____________________  corner 2
                   |                   |
                   |                   |
        line 0     |                   |  line 2
                   |                   |
                   |                   |
        corner 0   --------------------- corner 1
                           line 1
        """

        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        # Move into px coordinates to avoid problems with nonlinear axes
        xmin, ymin = self.datatopx((xmin, ymin))
        xmax, ymax = self.datatopx((xmax, ymax))

        if position is None:
            w, h = .5, .5  # relative initial width/height of rectangle in axes
            x_left = (1 - w) / 2 * (xmax - xmin) + xmin
            x_right = (1 + w) / 2 * (xmax - xmin) + xmin
            y_low = (1 - h) / 2 * (ymax - ymin) + ymin
            y_high = (1 + h) / 2 * (ymax - ymin) + ymin
        else:
            x0, y0, width, height = position
            x_left, y_low = self.datatopx((x0, y0))
            x_right, y_high = self.datatopx((x0 + width, y0 + height))

        x_center = (x_left + x_right) / 2
        y_center = (y_low + y_high) / 2

        pos1 = self.pxtodata((x_left, y_low))
        pos2 = self.pxtodata((x_right, y_low))
        pos3 = self.pxtodata((x_right, y_high))
        pos4 = self.pxtodata((x_left, y_high))
        posc = self.pxtodata((x_center, y_center))

        return pos1, pos2, pos3, pos4, posc

    @staticmethod
    def corners_to_edge(icorner1, icorner2):
        """Find the edge associated with two corners"""
        icorners = set([icorner1, icorner2])
        nozero = icorners - {0}
        if len(nozero) == 1:
            val, = nozero
            output = 1 if val == 1 else 0
        else:
            output = max(nozero)
        return output

    @staticmethod
    def edges_to_corner(iline1, iline2):
        """Find the corner associated with two edge lines"""
        ilines = set([iline1, iline2])
        nozero = ilines - {0}
        if len(nozero) == 1:
            val, = nozero
            output = 3 if val == 3 else 0
        else:
            output = min(nozero)
        return output

    def get_position(self):
        """Get position (xmin, ymin, width, height) in data coordinates."""
        xs, ys = [], []
        corners = self.all_artists[:4]
        for pt in corners:
            x, y = self.get_pt_position(pt, 'data')
            xs.append(x)
            ys.append(y)
        try:
            xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        except ValueError:
            raise ValueError('Impossible to get position of Rect, probably '
                             'because it has been deleted from the figure or '
                             'because figure itself has been closed.')
        w, h = xmax - xmin, ymax - ymin
        return xmin, ymin, w, h

    def _set_center_mode(self):
        """Given a selected line index, determine mode and active lines/pts."""
        lines = self.all_artists[4:-1]

        self.active_info = {'pts': self.all_pts,
                            'lines': lines,
                            'mode': 'center'}

    def _set_edge_mode(self, iline):
        """Given a selected line index, determine mode and active lines/pts."""

        corners = self.all_artists[:4]  # not all_pts, which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]

        line = lines[iline]

        # Distinguish whether line picked is vertical or horizontal
        mode = 'horz_edge' if iline % 2 else 'vert_edge'

        # neighbors of that line
        inext = (iline + 1) % 4
        iprev = (iline - 1) % 4
        active_lines = [line, lines[inext], lines[iprev]]

        # points connected to that line
        active_pts = [corners[iprev], corners[iline], center]

        self.active_info = {'pts': active_pts,
                            'lines': active_lines,
                            'mode': mode}

    def _set_corner_mode(self, icorner):
        """Given a selected corner, figure out active lines/pts."""

        corners = self.all_artists[:4]  # not all_pts, which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]

        iprev = (icorner - 1) % 4
        inext = (icorner + 1) % 4

        active_pts = [corners[icorner], corners[iprev], corners[inext], center]
        active_lines = lines  # all lines need to be updated in corner motion
        mode = icorner  # in the corner mode, the mode is identidied by its number

        self.active_info = {'pts': active_pts,
                            'lines': active_lines,
                            'mode': mode}

    def set_active_info(self):
        """Set active/inactive points during motion and detect motion mode."""

        corners = self.all_artists[:4]  # not all_pts, which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]

        # set which points are active and corresponding motion mode ----------

        if center in self.picked_artists:
            # center has been picked --> solid body motion
            self._set_center_mode()

        else:
            # Need to figure out which lines and corners have been picked
            picked_corners = set.intersection(self.picked_artists, corners)
            ncorners = len(picked_corners)

            if ncorners > 2:
                # If for some reason (e.g. overlap) this happens, also do
                # solid-body motion
                self._set_center_mode()

            elif ncorners == 2:
                # This is also an overlapping situation where two corners
                # correponding to an edge are selected --> edge motion
                icorners = [corners.index(pt) for pt in picked_corners]
                iline = self.corners_to_edge(*icorners)
                self._set_edge_mode(iline)

            elif ncorners == 1:
                # Just one corner picked: corner motion, move corresponding two edges
                corner, = picked_corners
                icorner = corners.index(corner)
                self._set_corner_mode(icorner)

            else:
                # No corner picked, but there might have been an edge line or more
                picked_lines = set.intersection(self.picked_artists, lines)
                nlines = len(picked_lines)
                print(nlines)

                if nlines == 1:
                    # Just one line: edge motion with that line
                    line, = picked_lines
                    i = lines.index(line)
                    self._set_edge_mode(i)

                elif nlines == 2:
                    # Two lines (and for some reason no corner): corner mode
                    ilines = [lines.index(line) for line in picked_lines]
                    icorner = self.edges_to_corner(*ilines)
                    self._set_corner_mode(icorner)

                elif nlines > 2:
                    # More than two lines: if this happens, whole object is kind of selected
                    self._set_center_mode()

                else:
                    # Normally, this case should never happen.
                    print('Warning: Rect.set_active_info() called while no artists '
                          'picked. Please report bug.')

    def update_position(self, event):
        """Update object position depending on moving mode and mouse position."""

        x, y = event.x, event.y  # pixel positions

        corners = self.all_artists[:4]  # not all_pts which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]

        active_pts = self.active_info['pts']
        active_lines = self.active_info['lines']
        mode = self.active_info['mode']

        if mode in ['horz_edge', 'vert_edge', 'center']:

            # get where click was initially made and calculate motion
            x0, y0 = self.press_info['click']
            dx = x - x0 if mode != 'horz_edge' else 0
            dy = y - y0 if mode != 'vert_edge' else 0

            for pt in active_pts:
                x0_pt, y0_pt = self.press_info[pt]
                if pt != center:
                    x_new, y_new = x0_pt + dx, y0_pt + dy
                else:   # center point
                    norm = 1 if mode == 'center' else 0.5
                    x_new = x0_pt + dx * norm
                    y_new = y0_pt + dy * norm
                self.moving_positions[pt] = x_new, y_new

        elif mode in range(4):  # corner motion

            i = mode
            picked_corner = corners[i]
            next_corner = corners[(i + 1) % 4]
            prev_corner = corners[(i - 1) % 4]
            opposite_corner = corners[(i + 2) % 4]

            self.moving_positions[picked_corner] = x, y
            xprev, yprev = self.moving_positions[prev_corner]
            xnext, ynext = self.moving_positions[next_corner]

            if i % 2:  # bottom right corner or top left
                self.moving_positions[prev_corner] = xprev, y
                self.moving_positions[next_corner] = x, ynext
            else:  # bottom left or top right corner
                self.moving_positions[prev_corner] = x, yprev
                self.moving_positions[next_corner] = xnext, y

            # Calculate center pos from picked pt and diagonally opposed one
            x1, y1 = self.moving_positions[picked_corner]
            x2, y2 = self.moving_positions[opposite_corner]
            self.moving_positions[center] = (x1 + x2) / 2, (y1 + y2) / 2

        # now apply the changes to the graph ---------------------------------
        for pt in active_pts:
            xnew, ynew = self.pxtodata(self.moving_positions[pt])
            pt.set_data(xnew, ynew)

        for line in active_lines:
            i = lines.index(line)
            x1, y1 = self.pxtodata(self.moving_positions[corners[i - 1]])
            x2, y2 = self.pxtodata(self.moving_positions[corners[i]])
            line.set_data([x1, x2], [y1, y2])

# ============================ callback functions ============================

    def on_key_press(self, event):
        if event.key == 'enter':
            print('Rectangle position recorded. Rectangle deleted.')
            self.recorded_position = self.get_position()
            self.delete()


# ======================== function rinput ===================================


def rinput(blit=True):
    """Select area of figure with interactive rectangle (enter to validate).

    Parameters
    ----------
    None at the moment. Options will be added soon.

    Returns
    -------
    4-tuple (xmin, ymin, width, height) of data coordinates.
    """
    r = Rect(block=True, blit=blit)
    try:
        position = r.recorded_position
    except AttributeError:
        print('Warning - Rectangle deleted before data validation. Returning None.')
        position = None
    return position
