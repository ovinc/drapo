"""Tests for the drapo module."""


from drapo.__main__ import main


import matplotlib
matplotlib.use('Qt5Agg')


def test_objects():
    """Test a bunch of interactive objects on a figure, including log plots."""
    try:
        main(blit=True, backend='Qt5Agg')
    except ValueError:
        main(blit=True, backend='TkAgg')


