"""Draggable Line on a Matplotlib Figure / Axes"""

# TODO: -- select subplot to draw in with a click
# TODO: -- interactive initiation of line position (with ginput or equivalent)
# TODO: -- add options of colors and style
# TODO: -- add double click to "freeze" line to avoid moving it by mistake later
# TODO: -- make program faster by saving canvas  before moving draglines (see matplotlib documentation)


import matplotlib.pyplot as plt
import numpy as np
import math as m


# ================================= example ==================================

def main():
    """ example of instances of draggable Lines in different figures and axes
    """
    fig, ax = plt.subplots()
    ax.plot([1, 0], [11, 13], '-r')

    drag = Line()

    fig2, ax2 = plt.subplots()
    tt = np.linspace(0, 4, 100000)
    xx = np.exp(-tt)
    ax2.plot(tt,xx,'-b')    

    drag2 = Line()

    fig3, (ax3, ax4) = plt.subplots(1, 2)
    ax3.plot(tt,xx)

    Line() 

    plt.show()


# ================================ line class ================================


class Line:
    """ Two dots connected by a line, draggable by its ends (the dots)"""

    
    draglines = [] # list of all instances of DragLines

    
    def __init__(self, position=(0.2, 0.2, 0.8, 0.8), fig=None, ax=None, pickersize=5):
        
        self.figure = plt.gcf() if fig==None else fig  # if no figure / axes specificed, use current ones
        self.axis  = plt.gca() if ax==None else ax
        
        self.xlim = self.axis.get_xlim()
        self.ylim = self.axis.get_ylim()
        
        x1, y1, x2, y2 = Line.set_position(self, position, pickersize)
        
        pt1, = self.axis.plot(x1, y1, '.k', picker=pickersize)
        pt2, = self.axis.plot(x2, y2, '.k', picker=pickersize)
        
        self.pt1 = pt1              # first point 
        self.pt2 = pt2              # second point
        self.line  = self.linecon(pickersize) # line connecting the points
        
        #self.pts = (self.pt1, self.pt2)
        self.all = (self.pt1, self.pt2, self.line)
        
        self.motionmode = None # indicates if object moves as a whole ('line') or with just one edge moving ('point'); is None when object not moving
        self.active = None    # active (moving) points: stores pt1 or pt2 in 'point' mode, stores 'all' in 'line' mode, stores None when not moving
        self.inactive = 'all' # inactive points       : stores pt2 or pt1 in 'point' mode, stores None  in 'line' mode, stores 'all' when not moving
        self.press = None # stores useful buttonpress info
        
        self.selected = set({}) # set that stores info about what parts of the line are selected (picked)
        
        self.connect() # connect to figure events
        
        Line.draglines.append(self)
        #print(f'{len(DragLine.draglines)} (init)')
        
        #self.figure.canvas.draw()  
        self.axis.set_xlim(self.xlim)
        self.axis.set_ylim(self.ylim)
        self.figure.show() # to pop up only figure where dragline is added

        
    def __repr__(self):
        drag_figures = [drag.figure for drag in Line.draglines]
        ndragonfig = drag_figures.count(self.figure)
        return f'Draggable Line #{ndragonfig} on Fig. {self.figure.number} \n'

    
    def __str__(self):
        return 'Draggable Line on Fig. {self.figure.number}'

    
    def set_position(self, position, pickersize):  
        """ sets position of new line, avoiding existing lines
        """
        mindist = 3*pickersize # minimum distance between points in pixels, to avoid overlapping
        maxloop = 1e3 # maximum number of loops to try to put the new instance in a good position
        
        ax = self.axis
        
        postopx = ax.transData # transform between data coordinates and pixel coordinates
        pxtopos = ax.transData.inverted() # pixels to data coordinates
        
        xmin, xmax = self.xlim
        ymin, ymax = self.ylim
        
        (a1, b1, a2, b2) = position
        
        x1, y1 = (1-a1)*xmin + a1*xmax, (1-b1)*ymin + b1*ymax # position lines at default position
        x2, y2 = (1-a2)*xmin + a2*xmax, (1-b2)*ymin + b2*ymax
        
        [X1, Y1] = postopx.transform((x1, y1))
        [X2, Y2] = postopx.transform((x2, y2))
        
        dragonax = []; # list of coordinates in pixels of existing draglines on the considered axes
        
        for drag in Line.draglines:
            
            if drag.axis is ax: # if on same axis, record coordinates in a list to check overlap later
                
                x1b, y1b = Line.get_pt_position(drag.pt1)
                x2b, y2b = Line.get_pt_position(drag.pt2)
                [X1b, Y1b] = postopx.transform((x1b, y1b))
                [X2b, Y2b] = postopx.transform((x2b, y2b))
                dragonax.append((X1b, Y1b))
                dragonax.append((X2b, Y2b))
                
        #print(f'existing draglines on axis: {int(len(dragonax)/2)}')      
        
        for i in range(int(maxloop)):
        
            for coords in dragonax:
                
                (Xb, Yb) = coords
                
                D1 = m.hypot(X1-Xb, Y1-Yb)
                D2 = m.hypot(X2-Xb, Y2-Yb)
                
                Dmin = min(D1, D2)
                
                if Dmin < mindist: # some of the points are too close
                    
                    X1 += -mindist # shift everything in a parallel manner
                    Y1 += +mindist
                    X2 += -mindist
                    Y2 += +mindist
                    
                    break

            else: break # for / else construction : if the inner for loop finishes, it means all points are ok, so break the main for loop
        else: print('Warning: Could not find suitable position for new DragLine')
        
        [x1, y1] = pxtopos.transform((X1, Y1)) # transformation back to data coordinates
        [x2, y2] = pxtopos.transform((X2, Y2))
                            
        return x1, y1, x2, y2

        
    @staticmethod
    def get_pt_position(pt):
        "Gets point position as a tuple from line data"
        xpt = pt.get_xdata()
        ypt = pt.get_ydata()
        
        x = xpt.item() # convert numpy array to scalar
        y = ypt.item()
        
        return x, y

        
    def linecon(self, pickersize):
        "connects two points with a line"
        
        x1, y1 = Line.get_pt_position(self.pt1)
        x2, y2 = Line.get_pt_position(self.pt2)
        
        ax = self.axis    
        l, = ax.plot([x1, x2], [y1, y2],'-k', picker = pickersize)
        
        return l


    def connect(self):      
        'connect object to figure canvas events'
        
        self.cidpress = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidpick = self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidaxleave = self.figure.canvas.mpl_connect('axes_leave_event', self.on_release) # consider that leaving axes is the same as releasing mouse
        self.cidclose = self.figure.canvas.mpl_connect('close_event', self.on_close)

        
    def on_pick(self, event):
        """if picked, save picked objects, or delete objects if right click
        """
        selected = event.artist
            
        if event.mouseevent.button==3 and (selected is self.line): # right click anywhere on the line, including ends, and it removes the line         
            self.remove_dragline()
            self.figure.canvas.draw()
            return
        
        if selected in self.all:
            self.selected.add(selected)
        
            
    def on_press(self, event):
        """once the selected points are known, on_press manages how to define active and inactive elements
        """
        if len(self.selected)==2: # in this case, one edge has been selected
            
            self.selected.remove(self.line) # remove the line to have only the point
            selected = self.selected.pop()  # extract the point, which should be the last element in the set
             
            self.active = selected # selected point becomes active
            self.inactive = self.inactive_select() # the other one is inactive
            self.inactpos = Line.get_pt_position(self.inactive) # store position of inactive point
        
            self.motionmode = 'point'
        
        if len(self.selected)==1:
            
            x1, y1 = Line.get_pt_position(self.pt1)
            x2, y2 = Line.get_pt_position(self.pt2)
            
            self.press = x1, y1, x2, y2, event.xdata, event.ydata # stores location of pts and of click
            self.active = 'all' 
            
            self.motionmode = 'line'

            
    def inactive_select(self):
        
        if self.active==None: return 'all'
        if self.active=='all': return None
        if self.active==self.pt1: return self.pt2
        if self.active==self.pt2: return self.pt1
    
    
    def on_motion(self, event):
        
        if self.motionmode==None: return
        
        x = event.xdata
        y = event.ydata
        
        if self.motionmode == 'point': # move just one point, the other one stays fixed
        
            x_inact, y_inact = self.inactpos
        
            self.active.set_xdata(x)  # update position of active point
            self.active.set_ydata(y)
            
            self.line.set_xdata([x, x_inact]) # update position of line
            self.line.set_ydata([y, y_inact])
            
            self.figure.canvas.draw()
            return
            
        if self.motionmode == 'line': # move the line as a whole in a parallel fashion
            
            x1, y1, x2, y2, xpress, ypress = self.press # get where click was initially made
            
            dx = x - xpress             # calculate motion
            dy = y - ypress
            
            self.pt1.set_xdata(x1+dx)
            self.pt1.set_ydata(y1+dy)
            
            self.pt2.set_xdata(x2+dx)
            self.pt2.set_ydata(y2+dy)
            
            self.line.set_xdata([x1+dx, x2+dx])
            self.line.set_ydata([y1+dy, y2+dy])
            
            self.figure.canvas.draw()
            return
            

    def on_release(self, event):
        
        self.motionmode = None
        self.active = None
        self.inactive = 'all'
        self.press = None
        self.selected = set({})
        
        
    def on_close(self, event):
        
        if self in Line.draglines:
            Line.draglines.remove(self)
            #print(f'{len(DragLine.draglines)} (close)')

        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        self.figure.canvas.mpl_disconnect(self.cidpick)
        self.figure.canvas.mpl_disconnect(self.cidaxleave)
        self.figure.canvas.mpl_disconnect(self.cidclose)

            
    def remove_dragline(self):
        
        self.pt1.remove()
        self.pt2.remove()
        self.line.remove()
        
        self.disconnect() # useful ?
        
        Line.draglines.remove(self)
        #print(f'{len(DragLine.draglines)} (delete)')
        
        del self
        
# ================================ direct run ================================
        
if __name__ == '__main__':
    main()

    