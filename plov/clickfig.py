"""Module to be able to select active figure and axes by clicking on them."""

# TODO -- add on_close where it disconnects only the closed figure ?
# TODO -- add method to remove / disconnect ClickFig
# TODO -- find better name for ClickFig
# TODO -- Track all instances and do not allow more than one at a time
# TODO -- Set maximum number of clicks

import matplotlib.pyplot as plt


def main():
    """Examples of figures to navigate arouund"""

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)

    ax2.set_facecolor('k')

    ax1.plot(1, 1, 'ok')

    fig2, ax3 = plt.subplots()

    ax3.plot(1, 1, '+r')
    
    plt.show(block=False)
    
    a = ClickFig()
    
    return a


class ClickFig:
    """Mouse that activates figures and axes by hovering and clicking"""

    fig_selectcolor = '#F3F8FA'
    ax_selectcolor = '#ECF4F8'

    def __init__(self):
        self.figs = ClickFig.list_figures()
        if len(self.figs) > 0:
            self.fig_colors, self.ax_colors = self.list_bgcolors()
            self.connect()
            # this seems to be a generic way to bring window to the front
            # but I have not checked with different backends etc.
            plt.get_current_fig_manager().show()
        else:
            print('No figure !')

    @staticmethod
    def list_figures():
        fignumbers = plt.get_fignums()
        print(fignumbers)
        figs = [plt.figure(f) for f in fignumbers]
        return figs

    def list_bgcolors(self):
        """lists and stores all background colors of figures and axes"""
        # store background colors (facecolor) of all figures in a dict
        fig_colors = {}
        # store background colors (facecolor) of all axes in a dict
        ax_colors = {}

        for fig in self.figs:
            fig_colors[fig] = fig.get_facecolor()
            for ax in fig.axes:
                ax_colors[ax] = ax.get_facecolor()

        return fig_colors, ax_colors
        
# ============================ callback functions ============================

    def on_fig_enter(self, event):
        fig = event.canvas.figure
        fig.set_facecolor(ClickFig.fig_selectcolor)
        fig.canvas.draw()


    def on_fig_leave(self, event):
        fig = event.canvas.figure
        original_color = self.fig_colors[fig]
        fig.set_facecolor(original_color)
        fig.canvas.draw()


    def on_ax_enter(self, event):
        fig = event.canvas.figure
        ax = event.inaxes
        ax.set_facecolor(ClickFig.ax_selectcolor)
        fig.canvas.draw()


    def on_ax_leave(self, event):
        fig = event.canvas.figure
        ax = event.inaxes
        original_color = self.ax_colors[ax] 
        ax.set_facecolor(original_color)
        fig.canvas.draw()


    def on_press(self, event):
        fig = event.canvas.figure
        ax = event.inaxes
    
        # activate clicked figure as the current figure.
        fnum = fig.number
        plt.figure(fnum)
        
        # activate clicked axes as the current axes.
        if ax is None:
            print('No axes on click location.')
        else:
            plt.sca(ax)
            print('Active axes defined.')

# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """Connect mouse events to all existing figures"""
        for fig in self.figs:
            self.enterfig_id = fig.canvas.mpl_connect('figure_enter_event', self.on_fig_enter)
            self.leavefig_id = fig.canvas.mpl_connect('figure_leave_event', self.on_fig_leave)
            self.enterax_id = fig.canvas.mpl_connect('axes_enter_event', self.on_ax_enter)
            self.leaveax_id = fig.canvas.mpl_connect('axes_leave_event', self.on_ax_leave)
            self.pressb_id = fig.canvas.mpl_connect('button_press_event', self.on_press)

    def disconnect(self):
        """Disconnect mouse events from all figures"""
        for fig in self.figs:
            fig.canvas.mpl_disconnect(self.enterfig_id)
            fig.canvas.mpl_disconnect(self.leavefig_id)
            fig.canvas.mpl_disconnect(self.enterax_id)
            fig.canvas.mpl_disconnect(self.leaveax_id)
            fig.canvas.mpl_disconnect(self.pressb_id)


# ================================ direct run ================================

if __name__ == '__main__':
    main()

