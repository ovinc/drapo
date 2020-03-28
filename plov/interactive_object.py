"""General object class, basis for Line and Rectangle"""


import matplotlib.pyplot as plt


class InteractiveObject:
    
    name = 'Interactive Object'
    all_objects = set()  # tracking all instances of the object

    def __init__(self, fig=None, ax=None):

        self.fig = plt.gcf() if fig is None else fig
        self.ax = plt.gca() if ax is None else ax

        # This is because adding lines can re-dimension axes limits
        self.xlim = self.ax.get_xlim()
        self.ylim = self.ax.get_ylim()
        
        self.all_objects.add(self)

        # this seems to be a generic way to bring window to the front but I
        # have not checked with all backends etc, and it does not always work
        plt.get_current_fig_manager().show()


    def __repr__(self):
        figs = [o.fig for o in self.__class__.all_objects]
        ndragonfig = figs.count(self.fig)
        name = self.__class__.name
        return f'{name} #{ndragonfig} on Fig. {self.fig.number}.'

    def __str__(self):
        name = self.__class__.name
        return f'{name} on Fig. {self.fig.number}.'
    
    
# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """connect object to figure canvas events"""
        # mouse events
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.cidpick = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)    
        #key events
        self.cidpressk = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        # figure events
        self.cidaxenter = self.fig.canvas.mpl_connect('axes_enter_event', self.on_enter_axes)
        self.cidaxleave = self.fig.canvas.mpl_connect('axes_leave_event', self.on_leave_axes)
        self.cidclose = self.fig.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        """disconnect callback ids"""    
        # mouse events
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidpick)
        # key events
        self.fig.canvas.mpl_disconnect(self.cidpressk)
        # figure events
        self.fig.canvas.mpl_disconnect(self.cidaxenter)
        self.fig.canvas.mpl_disconnect(self.cidaxleave)
        self.fig.canvas.mpl_disconnect(self.cidclose)


# ============================ callback functions ============================


    # mouse events 
    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_release(self, event):
        pass
    
    def on_pick(self, event):
        pass
 
    def on_motion(self, event):
        pass
    
    # key events
    
    def on_key_press(self, event):
        pass

    # figure events
    
    def on_enter_axes(self, event):
        pass

    def on_leave_axes(self, event):
        pass

    def on_close(self, event):
        pass
    
    


