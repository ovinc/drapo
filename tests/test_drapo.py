"""Tests for the drapo module."""

import matplotlib.pyplot as plt
import numpy as np

import drapo

import matplotlib
matplotlib.use('Qt5Agg')

def test_objects():
    """Test a bunch of interactive objects on a figure, including log plots."""
    fig1, ax1 = plt.subplots()

    # Draw a bunch of static objects on the figure for visual references -----

    tt = np.linspace(0, 4, 10000)
    xx = np.exp(-tt)
    ax1.plot(tt, xx, '-b', c='lightblue', linewidth=4)

    ax1.set_xscale('log')
    ax1.set_yscale('log')

    # Add an interactive line and an interactive rectangle -------------------

    l1 = drapo.Line(blit=False)  # blit=False should be cancelled by the last line (see below)
    r1 = drapo.Rect(linewidth=2, color='firebrick')

    # Second figure with static objects on different subplots ----------------

    z = np.random.randn(1000)

    fig2, (ax2a, ax2b) = plt.subplots(1, 2)
    ax2a.plot(tt, xx)
    ax2b.plot(z, '-ob', c='tan')

    ax2a.set_yscale('log')

    # Add other Lines --------------------------------------------------------

    l2 = drapo.Line(ax=ax2a, color='r', ptstyle='s')   # put lines on different subplots
    l3 = drapo.Line(ax=ax2b)

    # this one is plot in current axes, and sets the blit behavior of all lines
    l4 = drapo.Line(blit=True, linewidth=2, ptstyle='o')

    # Add a cursor (should follow the mouse on all figs/axes) ----------------

    c = drapo.Cursor()

    plt.show()
