"""Demo of several objects, functions and their features."""

import argparse

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from . import Line, ginput, rinput, Cursor


def demo_figure():
    """Create demo fig and axes."""

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(9, 4)

    npts = 1000

    tt = np.linspace(0, 4, npts)
    rr = np.random.randn(npts)
    xx = np.exp(-tt) + 0.1 * rr

    ax1.set_yscale('log')

    ax1.plot(tt, xx, '.', c='lightsteelblue')
    ax2.plot(rr, '-o', c='lightsteelblue')

    fig.set_facecolor('gainsboro')

    return fig, (ax1, ax2)


def demo(blit=True, backend=None):
    """Example of various objects in different figures and axes (for testing)."""

    if backend is not None:
        matplotlib.use(backend)

    print('Blitting', blit, 'Backend', matplotlib.get_backend())

    # Demo of Cursor and ginput()

    fig, (ax1, ax2) = demo_figure()

    fig.suptitle('Cursor() and ginput()', fontsize=16)
    data = ginput(4, blit=blit)
    print(f'{len(data)} recorded clicks: ', data)

    fig.suptitle('Rect() and rinput()', fontsize=16)
    data = rinput(blit=blit)
    print('recorded rectangle (x, y, w, h): ', data)

    fig.suptitle('Line()', fontsize=16)
    Line(c='k', linewidth=2, ptstyle='s', ptsize=8)
    Line(c='seagreen', linewidth=4)

    Cursor()

    # The last object imposes blitting behavior of all objects
    Line(linestyle='--', linewidth=1, ptstyle='o', blit=blit)

    plt.show()


if __name__ == '__main__':

    descr = "Run demo for drapo, with backend and blitting options."

    parser = argparse.ArgumentParser(
        description=descr,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    msg = "(str): Matplotlib backend (e.g. 'TkAgg', 'Qt5Agg', 'MacOSX', etc.)"
    parser.add_argument('-B', '--backend', type=str, help=msg)

    msg = "(True or False): use blitting for fast rendering (default True)"
    parser.add_argument('-b', '--blit', type=str, default='True', help=msg)

    args = parser.parse_args()

    blit = True if args.blit == 'True' else False

    demo(blit=blit, backend=args.backend)
