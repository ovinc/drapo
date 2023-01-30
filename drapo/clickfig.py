"""Module to be able to select active figure and axes by clicking on them."""

# TODO -- add on_close behavior (e.g. disconnect, but only on the closed fig)
# TODO -- similarly, disconnect when the last figure is closed ? I don't know if this is useful
# TODO -- use key shortcuts to validate / cancel
# TODO -- add function that returns the selected ax/fig (probably needs block)


import matplotlib
import matplotlib.pyplot as plt


# ================================= Testing ==================================

def main(backend=None):

    if backend is not None:
        matplotlib.use(backend)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)

    ax2.set_facecolor('k')

    ax1.plot(1, 1, 'ok')

    fig2, ax3 = plt.subplots()

    ax3.plot(1, 1, '+r')

    plt.show(block=False)

    ClickFig()


# ============================== ClickFig class ==============================


class ClickFig:
    """Mouse that activates figures and axes by hovering and clicking.

    - Left Click on figure / axes to make them the current ones in Matplotlib.
    - Right Click anywhere to deactivate the interactive mouse.

    Parameters
    ----------
    - n (int, default 1): maximum number of clicks allowed.
    - highlight (bool, default True): change ax/fig color when mouse on them.
    - `verbose` (bool, default False). If True, some events associated with
                interactive objects are printed in the console.
    """

    fig_selectcolor = '#F3F8FA'
    ax_selectcolor = '#ECF4F8'

    clickfigs = []  # tracks all instances of ClickFig

    def __init__(self, n=1, highlight=True, verbose=False):

        self.figs = ClickFig.list_figures()

        self.n = n
        self.highlight = highlight
        self.verbose = verbose

        if len(self.figs) > 0:

            self.active_fig = plt.gcf()
            self.active_ax = plt.gca()

            self.fig_colors, self.ax_colors = self.list_bgcolors()

            self.clicknumber = 0

            ClickFig.clickfigs.append(self)

            self.connect()

        else:
            raise FigureError("No existing Matplotlib figure!")

    @staticmethod
    def list_figures():
        fignumbers = plt.get_fignums()
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

    def erase(self):
        self.disconnect()

# ============================= callback methods =============================

    def on_fig_enter(self, event):
        if self.highlight is True:
            fig = event.canvas.figure
            fig.set_facecolor(ClickFig.fig_selectcolor)
            fig.canvas.draw()

    def on_fig_leave(self, event):
        if self.highlight is True:
            fig = event.canvas.figure
            original_color = self.fig_colors[fig]
            fig.set_facecolor(original_color)
            fig.canvas.draw()

    def on_ax_enter(self, event):
        if self.highlight is True:
            fig = event.canvas.figure
            ax = event.inaxes
            ax.set_facecolor(ClickFig.ax_selectcolor)
            fig.canvas.draw()

    def on_ax_leave(self, event):
        if self.highlight is True:
            fig = event.canvas.figure
            ax = event.inaxes
            original_color = self.ax_colors[ax]
            ax.set_facecolor(original_color)
            fig.canvas.draw()

    def on_press(self, event):
        fig = event.canvas.figure
        ax = event.inaxes

        if event.button == 1:  # left click : activate ax/fig

            self.clicknumber += 1

            # activate clicked figure as the current figure.
            fnum = fig.number
            plt.figure(fnum)

            # activate clicked axes as the current axes.
            if ax is None:
                if self.verbose:
                    print('\nActive Figure defined, no Axes on click location.')
            else:
                plt.sca(ax)
                if self.verbose:
                    print('\nActive Figure and Axes defined.')

        # right click or reached max click number: deactivate interactive mouse
        if event.button == 3 or self.clicknumber == self.n:

            original_color = self.fig_colors[fig]
            fig.set_facecolor(original_color)
            fig.canvas.draw()

            if ax is not None:
                original_color = self.ax_colors[ax]
                ax.set_facecolor(original_color)
                fig.canvas.draw()

            if event.button == 3:
                if self.verbose:
                    print('\nClickFig deactivated (left click).')
            else:
                if self.verbose:
                    print('\nClickFig deactivated (max number of clicks reached).')

            self.erase()

    def on_close(self, event):
        pass
        # self.erase()

# ================= connect/disconnect events and callbacks ==================

    def connect(self):
        """Connect mouse events to all existing figures"""
        for fig in self.figs:
            self.enterfig_id = fig.canvas.mpl_connect('figure_enter_event', self.on_fig_enter)
            self.leavefig_id = fig.canvas.mpl_connect('figure_leave_event', self.on_fig_leave)
            self.enterax_id = fig.canvas.mpl_connect('axes_enter_event', self.on_ax_enter)
            self.leaveax_id = fig.canvas.mpl_connect('axes_leave_event', self.on_ax_leave)
            self.pressb_id = fig.canvas.mpl_connect('button_press_event', self.on_press)
            self.close_id = fig.canvas.mpl_connect('close_event', self.on_close)

    def disconnect(self):
        """Disconnect mouse events from all figures"""
        for fig in self.figs:
            fig.canvas.mpl_disconnect(self.enterfig_id)
            fig.canvas.mpl_disconnect(self.leavefig_id)
            fig.canvas.mpl_disconnect(self.enterax_id)
            fig.canvas.mpl_disconnect(self.leaveax_id)
            fig.canvas.mpl_disconnect(self.pressb_id)
            fig.canvas.mpl_disconnect(self.close_id)


# =========================== custom Figure Error ============================


class FigureError(Exception):
    """Raised when there are no existing figures."""
    pass


# ================================ direct run ================================


if __name__ == '__main__':
    main()
