# plov -- Extra interactive Matplotlib features

## Documentation

### Line class

- Creates a draggable line on a matplotlib figure/axes.
- Right-click to remove line.
- If mouse leaves axes, control over the line is lost.

To initiate a line, just use `Line()`

### Cursor class
- Creates a cursor (vertical+horizontal dashed lines) that moves with the mouse
- Upon clicking, shows info on the click location.
- Cursor is not initiated if the figure has no axes

To initiate a cursor, just use `Cursor()`

## Module requirements
- matplotlib
- numpy

## Python requirements
Python : >= 3.6