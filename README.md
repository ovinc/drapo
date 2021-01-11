# About

**drapo** (*draggable plot objects*) is a Python 3 package that provides a set of interactive graphical objects on Matplotlib figures: draggable line, draggable rectangle, moving cursor, and interactive click to define active figure/axes.

Based on these tools, the package also provides graphical input functions for measuring/extracting data interactively from a figure, such as ginput (get location of clicks) and rinput (get region of interest from interactive rectangle).

Matplotlib must be using an interactive backend such as Qt or Tk. In Jupyter, use `%matplotlib qt` or `%matplotlib tk` (or simply `%matplotlib`).

### Draggable shapes
- **Line** is a class that creates a draggable line.
- **Rect** is a class that creates a draggable rectangle.

### Moving cursor
- **Cursor** is a class that creates a cursor that follows the mouse

### Graphical input functions
- **ginput** is a function based on the Cursor class that returns position data from clicks/keystrokes.
- **rinput** is a function based on the Rect class that returns position data delimited by an interactive rectangle.

### Other
- **ClickFig** is a class that activates figures and axes (makes them the current ones) by mouse hovering and clicking.

Below is an illustration of instances of Line (left, black), Rect (left, red), Cursor (right, green). The current mouse position is at the center of the cursor.

![](https://raw.githubusercontent.com/ovinc/drapo/master/media/example.jpg)


# Install

```bash
pip install drapo
```


# Quick start

Below is a brief overview on how to use the package contents with the most basic features. For full documentation, see *DOCUMENTATION.md*. For background code and development info, see *DEVELOPMENT.md*.

```python
from drapo import Line, Cursor, Rect, ClickFig, ginput, rinput
```

## Draggable objects

`Line()` creates a line in the current axes of the current figure (creates new figure if none existing) that is draggable by left-clicking on it. Motion is different whether click is done on the line ends or on the line itself. To remove the line, right-click on it.

`Rect()` creates a draggable rectangle in the current or specified figure. Motion is triggered by left-clicking on the edges (lines), vertices (corner points), or in the center (marked by a cross). Right-click to delete.

See documentation for options to change the appearance of these objects.
See ClickFig below to activate axes interactively to be able to create the objects in specific axes as needed.

## Moving cursor

`Cursor()` creates a cursor in the current figure, but contrary to the draggable objects, the cursor is not bound to specific axes. It is however bound to a figure, and will appear on whatever axes the mouse is currently on; it will switch axes if the mouse goes over other axes. No cursor is visible if the mouse is not currently on axes.
- Use <kbd>⇧ Shift</kbd> + left/right arrow keys to change color.
- Use <kbd>⇧ Shift</kbd> + up/down keys to change thickness.
- Use the <kbd>space</kbd> bar to toggle visibility on/off.

## Graphical input functions

`ginput()` will return the data coordinates (x, y) of one click on any axes of the current figure.
- Use `ginput(n)` to record exactly n data points (returns list of tuples).
- Use `ginput(-1)` for an undefined amount of points.
- Left click or press <kbd>a</kbd> to add point.
- Right click or press <kbd>z</kbd> to remove point.
- Middle click or press <kbd>enter</kbd> to finish input.

`rinput()` will instantiate an interactive rectangle and return its position as a tuple (xmin, ymin, width, height) when the <kbd>enter</kbd> key is pressed.

## Activate specific figure/axes (ClickFig)

Sometimes the current figure/axes are not the ones where one wants to create the objects. To solve this problem, it is possible to use the ClickFig class.

`ClickFig()` will make all existing figures and axes clickable (hovering the mouse should highlight the fig/ax under it with a light blue color). Simply left-click in the ones you would like to activate. By default, activation stops after one click.

`ClickFig(-1)` will keep all fig/ax active for an undefined amount of clicks. Since ClickFig is non-blocking, this is a way to be able to be able to keep activating axes during a work session, without having to instantiate a ClickFig every time. In this situation, deactivation of the ClickFig is done by right-click.

`ClickFig(highlight=False)` allows not using color highlighting of the fig/ax if it is bothersome.


# Tips and Troubleshooting

If the package does not work, try the following hacks:
- If instantiating from the command line, Matplotlib figures need to not block the console. For this, use `plt.show(block=False)` when creating the figure.
- Try another interactive action on the figure such as zooming/panning to see if it makes the objects miraculously appear.
- Use a different matplotlib backend. In particular, *MacOSX* seem to cause problems where nothing is drawn or where the figure crashes. Try e.g. `matplotlib.use('Qt5Agg')`, `matplotlib.use('Qt4Agg')` or `matplotlib.use('TkAgg')`.
- Similarly, in Jupyter, an interactive backend needs to be used, with the command `%matplotlib qt` or `%matplotlib tk` (or simply `%matplotlib`).
- Pass `blit=False` in the argument of any class or function (except ClickFig) to see if the problem comes from the blitting strategy used for fast rendering.

# Requirements

## Packages

- matplotlib (automatically installed by pip if necessary)
- numpy (optional, only needed to run the examples present in the main() functions)

## Python

Python : >= 3.6

# Author

Olivier Vincent

(ovinc.py@gmail.com)

# License

3-Clause BSD (see *LICENSE* file).