"""Interactive, draggable rectangle on matplotlib figure."""

# TODO -- Add blocking behavior to be able to define cropzones etc.
# TODO -- Add option for appearance of center


import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from .interactive_object import InteractiveObject


def main(blit=True, backend=None):  # For testing purposes
    
    if backend is not None:
        matplotlib.use(backend)
    
    fig1, ax1 = plt.subplots()
    tt = np.linspace(0, 4, 100000)
    xx = np.exp(-tt)
    ax1.plot(tt, xx, '-b')
    
    #ax1.set_xscale('log')
    #ax1.set_yscale('log')

    r1 = Rect()

    plt.show(block=False)
    
    return r1
        

class Rect(InteractiveObject):
    """Interactive draggable rectangle on matplotlib figure/axes.
    
    Left click to drag rectangle, right click to remove it. Clicking can be
    done on the edges, vertices (corners), or on the center. These clicks
    trigger different modes of motion.
    
    Parameters
    ----------
    All parameters optional so that a rectangle can be created by `Rect()`.

    - `fig` (matplotlib figure, default: current figure, specified as None).
    - `ax` (matplotlib axes, default: current axes, specified as None).
    - 'pickersize' (float, default: 5), tolerance for object picking.
    - `color` (matplotlib's color, default: None (class default value)).

    Appearance of the vertices (corners):
    - `ptstyle` (matplotlib's marker, default: dot '.').
    - `ptsize` (float, default: 5). Marker size.

    Appearance of the edges (lines):
    - `linestyle` (matplotlib's linestyle, default: continuous '-').
    - `linewidth` (float, default: 1). Line width.
    
    Other
    - `blit` (bool, default True). If True, blitting is used for fast rendering
    - `block`(bool, default False). If True, object blocks the console
    (block not implemented yet for Line and Rect)
    """
    
    name = "Draggable Rectangle"

    
    def __init__(self, fig=None, ax=None, pickersize=5, color='r',
                 ptstyle='.', ptsize=5, linestyle='-', linewidth=1,
                 blit=True, block=False):
        
        super().__init__(fig=fig, ax=ax, color=color, blit=blit, block=block)
        
        options = (pickersize, color, ptstyle, ptsize, linestyle, linewidth)
        self.create(options)
        
        # to prevent any shift in axes limits when instanciating line. The
        # initial self.xlim / self.ylim setting is done in InteractiveObject
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        
        self.fig.canvas.draw()
        
        
    def create(self, options):
        
        (pickersize, color, ptstyle, ptsize, linestyle, linewidth) = options

        positions = self.set_initial_position()
        corner_positions = positions[:-1]  # the last one is the center
        
        # Create all vertices (corners) of the rectangle ---------------------
        corners = []
        for pos in corner_positions:
            pt, = self.ax.plot(*pos, marker=ptstyle, color=color,
                               markersize=ptsize, picker=pickersize)
            corners.append(pt)
            
        # Create all lines (edges) of the rectangle --------------------------
        lines = []
        for i, pos in enumerate(corner_positions):
            x1, y1 = corner_positions[i-1]
            x2, y2 = pos
            line, = self.ax.plot([x1, x2], [y1, y2], c=color, 
                                 picker=pickersize,
                                 linestyle=linestyle, linewidth=linewidth)
            lines.append(line)
            
        # Create center of rectangle -----------------------------------------
        x_center, y_center = positions[-1]
        center, = self.ax.plot(x_center, y_center, marker='+', color=color,
                               markersize=10, picker=pickersize)
        
        self.all_artists = (*corners, *lines, center)
        self.all_pts = (*corners, center)
    
    
    def set_initial_position(self):
        """Set position of new line, avoiding existing lines if necessary."""
        
        xmin, xmax = self.xlim
        ymin, ymax = self.ylim
        
        w = 0.5 # relative width of rectangle compared to axes
        h = 0.5 # relative height
        
        x_left = (1 - w) / 2 * (xmax - xmin) + xmin
        x_right = xmax - x_left
        
        y_low = (1 - h) / 2 * (ymax - ymin) + ymin
        y_high = ymax - y_low
        
        x_center = (x_left + x_right) / 2
        y_center = (y_low + y_high) / 2
        
        pos1 = (x_left, y_low)
        pos2 = (x_right, y_low)
        pos3 = (x_right, y_high)
        pos4 = (x_left, y_high)
        posc = (x_center, y_center)
        
        return pos1, pos2, pos3, pos4, posc
    
    
    def set_active_info(self):
        """separates points into active/inactive and detects motion mode"""
        
        corners = self.all_artists[:4]  # not all_pts which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]
        
        # set which points are active and corresponding motion mode ----------
        
        if len(self.picked_artists) == 1:  # edge selected
            
            [pickedline] = self.picked_artists
            
            if pickedline == center:  # center has been picked --> solid body motion
                mode = 'center'
                active_lines = lines
                active_pts = self.all_pts
            
            else:  # one of the edges selected --> move that eddge only
            
                i = lines.index(pickedline)
                # Distinguish whether line picked is vertical or horizontal
                mode = 'horz_edge' if i%2 else 'vert_edge'
                
                # neighbors of that line
                inext = (i+1)%4
                iprev = (i-1)%4         
                active_lines = [pickedline, lines[inext], lines[iprev]]
                
                # points connected to that line
                active_pts = [corners[iprev], corners[i], center]
            
            
        elif len(self.picked_artists) == 3:  # corner selected --> move corresponding two edges
            
            # find which corner has been selected and set its index as the mode
            for i, pt in enumerate(corners):
                if pt in self.picked_artists:
                    mode = i
            
            i = mode
            iprev = (i-1)%4
            inext = (i+1)%4
            
            active_pts = [corners[i], corners[iprev], corners[inext], center]
            active_lines = lines  # all lines need to be updated in corner motion
            
        else:  # Normally, this should not happen
            mode = None
                 
        self.active_info =  {'active_pts': active_pts, 
                             'active_lines': active_lines, 
                             'mode': mode}


    def update_position(self, event):
        """Update object position depending on moving mode and mouse position."""
        
        x = event.x   # pixel positions
        y = event.y
        
        corners = self.all_artists[:4]  # not all_pts which can contain additional tracking pts
        lines = self.all_artists[4:-1]
        center = self.all_artists[-1]
        
        active_pts = self.active_info['active_pts']
        active_lines = self.active_info['active_lines']
        mode = self.active_info['mode']
        
        if mode in ['horz_edge', 'vert_edge', 'center']:
            
            # get where click was initially made and calculate motion
            x_press, y_press = self.press_info
            dx = x - x_press['click'] if mode != 'horz_edge' else 0
            dy = y - y_press['click'] if mode != 'vert_edge' else 0
            
            for pt in set(active_pts):
                if pt != center:
                    x_new = x_press[pt] + dx
                    y_new = y_press[pt] + dy
                else:   # center point
                    norm = 1 if mode =='center' else 0.5
                    x_new = x_press[pt] + dx * norm
                    y_new = y_press[pt] + dy * norm
                x_data, y_data = self.pxtodata((x_new, y_new))
                self.x_inmotion[pt] = x_data
                self.y_inmotion[pt] = y_data     
                
        elif mode in range(4):  # corner motion
        
            i = mode
            picked_corner = corners[i]
            next_corner = corners[(i+1)%4]
            prev_corner = corners[(i-1)%4 ]
            opposite_corner = corners[(i+2)%4 ]  
 
            x_data, y_data = self.pxtodata((x, y))
            self.x_inmotion[picked_corner] = x_data
            self.y_inmotion[picked_corner] = y_data
            
            xref, yref = self.get_pt_position(picked_corner)
            
            if i%2:  # bottom right corner or top left
                self.y_inmotion[prev_corner] = y_data
                self.x_inmotion[next_corner] = x_data
            else:  # bottom left or top right corner
                self.x_inmotion[prev_corner] = x_data
                self.y_inmotion[next_corner] = y_data
                
            self.x_inmotion[center] = (self.x_inmotion[picked_corner] +
                                       self.x_inmotion[opposite_corner]) / 2
            self.y_inmotion[center] = (self.y_inmotion[picked_corner] +
                                       self.y_inmotion[opposite_corner]) / 2
            
        # now apply the changes to the graph ---------------------------------
        for pt in active_pts:
            pt.set_xdata(self.x_inmotion[pt])
            pt.set_ydata(self.y_inmotion[pt])
        
        for line in active_lines:
            i = lines.index(line)
            pt1 = corners[i]
            pt2 = corners[i-1]
            line.set_xdata([self.x_inmotion[pt1], self.x_inmotion[pt2]])
            line.set_ydata([self.y_inmotion[pt1], self.y_inmotion[pt2]])
        
            
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