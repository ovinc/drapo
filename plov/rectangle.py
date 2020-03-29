"""Interactive, draggable rectangle on matplotlib figure."""

from plov import Line

#from .interactive_object import InteractiveObject



class Rect(Line):
    """Draggable rectangle, based on the plov.Line class"""
    
    name = "Draggable Rectangle"
    all_objects = set()
    
    def __init__(self, fig=None, ax=None, blit=True,
                 pickersize=5, color=None,
                 ptstyle='.', ptsize=5,
                 linestyle='-', linewidth=1):
        
        super().__init__(fig=fig, ax=ax, blit=blit, pickersize=pickersize, 
                         color=color, ptstyle=ptstyle, ptsize=ptsize, 
                         linestyle=linestyle, linewidth=linewidth)
        
        
        self.connect()
        
    def create(self, options):
        
        # DO NOT change this, as it must be the same as in Line class
        (pos, pickersize, color, ptstyle, ptsize, 
         linestyle, linewidth, avoid_existing) = options
            
        w = 0.5
        h = 0.5
        
        x_left = (1 - w) / 2
        x_right = 1 - x_left
        
        y_low = (1 - h) / 2
        y_high = 1 - y_low
        
        # Create all four corners (vertices) of the rectangle ----------------
        
        pos1 = (x_left, y_low)
        pos2 = (x_right, y_low)
        pos3 = (x_right, y_high)
        pos4 = (x_left, y_high)
        
        positions = (pos1, pos2, pos3, pos4)
        
        corners = []
        
        for pos in positions:
            pt, = self.ax.plot(*pos, marker=ptstyle, color=color,
                               markersize=ptsize, picker=pickersize)
            corners.append(pt)
            
        # Create all lines (edges) of the rectangle --------------------------
        
        lines = []
        
        for i, pos in enumerate(positions):
            x1, y1 = positions[i-1]
            x2, y2 = pos
            line, = self.ax.plot([x1, x2], [y1, y2], c=color, 
                                 picker=pickersize,
                                 linestyle=linestyle, linewidth=linewidth)
            lines.append(line)
        
        self.corners = tuple(corners)
        self.lines = tuple(lines)
        self.all = (*corners, *lines)
            
            
# ============================ callback functions ============================

    # mouse events 
    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_release(self, event):
        pass
    
    def on_motion(self, event):
        pass
    


    # figure events
    
    def on_enter_axes(self, event):
        pass

    def on_leave_axes(self, event):
        pass

    def on_close(self, event):
        pass
    
    
    
if __name__ == '__main__':
    Rect()
        
            
        
