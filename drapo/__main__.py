"""Main module for  mainly for testing"""


import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from . import Line, Rect, Cursor

# ================================= Testing ==================================


def main(blit=True, backend=None):
    """Example of various objects in different figures and axes (for testing)."""

    if backend is not None:
        matplotlib.use(backend)

    # Draw a bunch of static objects on the figure for visual references -----

    fig1, ax1 = plt.subplots()

    tt = np.linspace(0, 4, 1000)
    xx = np.exp(-tt)
    ax1.plot(tt, xx, '-', c='lightblue', linewidth=5)

    ax1.set_xscale('log')
    ax1.set_yscale('log')

    # Add an interactive line and an interactive rectangle -------------------

    l1 = Line(blit=False)  # blit=False should be cancelled by the last line (see below)
    r1 = Rect(linewidth=2)

    # Second figure with static objects on different subplots ----------------

    z = np.random.randn(1000)

    fig2, (ax2a, ax2b) = plt.subplots(1, 2)
    ax2a.plot(tt, xx)
    ax2b.plot(z, '-o', c='lightsteelblue')

    ax2a.set_yscale('log')

    # Add other Lines --------------------------------------------------------

    l2 = Line(ax=ax2a, color='royalblue', ptstyle='s')
    l3 = Line(ax=ax2b)

    # this one is plot in current axes, and sets the blit behavior of all lines
    l4 = Line(blit=blit, linewidth=2, ptstyle='o')

    # Add a cursor (should follow the mouse on all figs/axes) ----------------

    c = Cursor()

    plt.show()

    return l1, r1, l2, l3, l4, c


if __name__ == '__main__':
    main()
