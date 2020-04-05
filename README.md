# Plot-OV (plov) - Additional interactive Matplotlib features


## General information

This Python 3 package provides a set of interactive graphical objects on matplotlib figures: draggable lines and rectangles, cursor, and associated useful functions such as ginput() for measuring/extracting data interactively.

### Draggable shapes
- **Line** is a class that creates a draggable line.
- **Rect** is a class that creates a draggable rectangle.

### Cursor and ginput
- **Cursor** is a class that creates a cursor that follows the mouse
- **ginput** is a function based on Cursor that returns data from clicks/keystrokes.

### Other
- **ClickFig** is a class that activates figures and axes (makes them the current ones) by mouse hovering and clicking.

## Install

For now the package is not listed in PyPI, so one needs to do a manual install.
Follow the steps below:

- Clone the project or download directly the files into a folder.
- In the command line, `cd` into the project or folder, you should see a file
  named __setup.py__.
- run `python -m pip install .`

Now, the package can be imported in Python with `import plov`.

**Note**: replace `python` with the command or alias corresponding to the Python installation you would like to install the package with.

**Note**: if you wish to keep the package files in the folder where the files
were downloaded and/or edit the files with direct effect in Python, run the
following install command instead: `python -m pip install -e .`.

## Quick start

Below is a brief overview on how to use the package contents with the most basic features. For full documentation, see *DOC.md*.

```python
from plov import Line, Cursor, Rect, ClickFig, ginput
```

### Draggable objects

`Line()` creates a line in the current axes of the current figure (creates new figure if none existing) that is draggable by left-clicking on it. Motion is different whether click is done on the line ends or on the line itself. To remove the line, right-click on it.

`Rect()` creates a draggable rectangle in the current or specified figure. Motion is triggered by left-clicking on the edges (lines), vertices (corner points), or in the center (marked by a cross). Right-click to delete.

See documentation for options to change the appearance of these objects.
See ClickFig below to activate axes interactively to be able to create the objects in specific axes as needed.

### Cursor and ginput (extract data from mouse position)

`Cursor()` creates a cursor in the current figure, but contrary to the draggable objects, the cursor is not bound to specific axes. It is however bound to a figure, and will appear on whatever axes the mouse is currently on; it will switch axes if the mouse goes over other axes. No cursor is visible if the mouse is not currently on axes. 
- Use <kbd>⇧ Shift</kbd> + left/right arrow keys to change color. 
- Use <kbd>⇧ Shift</kbd> + up/down keys to change thickness.
- Use the <kbd>space</kbd> bar to toggle visibility on/off.

`ginput()` will return the data coordinates of one click on any axes of the current figure.
- Use `ginput(n)` to record exactly n data points.
- Use `ginput(-1)` for an undefined amount of points.
- Left click or press <kbd>a</kbd> to add point.
- Right click or press <kbd>z</kbd> to remove point.
- Middle click or press <kbd>enter</kbd> to finish input.

### Activate specific figure/axes (ClickFig)

Sometimes the current figure/axes are not the ones where one wants to create the objects. To solve this problem, it is possible to use the ClickFig class.

`ClickFig()` will make all existing figures and axes clickable (hovering the mouse should highlight the fig/ax under it with a light blue color). Simply left-click in the ones you would like to activate. By default, activation stops after one click.

`ClickFig(-1)` will keep all fig/ax active for an undefined amount of clicks. Since ClickFig is non-blocking, this is a way to be able to be able to keep activating axes during a work session, without having to instantiate a ClickFig every time. In this situation, deactivation of the ClickFig is done by right-click.

`ClickFig(highlight=False)` allows not using color highlighting of the fig/ax if it is bothersome.


## Tips and Troubleshooting

If the package does not work, try the following hacks:
- If instantiating from the command line, Matplotlib figures need to not block the console. For this, use `plt.show(block=False)` when creating the figure.
- Try another interactive action on the figure such as zooming/panning to see if it makes the objects miraculously appear.
- Use a different matplotlib backend. In particular, *TkAgg* and *MacOSX* seem to cause problems where nothing is drawn or where the figure crashes. Try e.g. `matplotlib.use('Qt5Agg')` or `matplotlib.use('Qt4Agg')`.
- Pass `blit=False` in the argument of any class or function (except ClickFig) to see if the problem comes from the blitting strategy used for fast rendering.
- Contact the author if problem persist.


## Module requirements

- matplotlib
- numpy (only needed to run the examples present in the main() functions)

## Python requirements

Python : >= 3.6 (because of f-strings)

## Author

Olivier Vincent
olivier.a-vincent@wanadoo.fr