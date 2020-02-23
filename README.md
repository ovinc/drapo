# plov -- Extra interactive Matplotlib features

## Documentation

### Line class

- Creates a draggable line on a matplotlib figure/axes.
- Right-click to remove line.
- If mouse leaves axes, control over the line is lost.

To initiate a line, just use `Line()`.
See help of the Line class for options.

### Cursor class

`Cursor(figure=None, color='r', style=':', blit=True, size=1, mark_clicks=False, record_clicks=False, click_button=1, mark_symbol='+', mark_size=10)`

This class creates a cursor that moves along with the mouse. It is drawn
only within existing axes, but contrary to the matplotlib widget Cursor,
is not bound to specific axes: moving the mouse over different axes will
plot the cursor in these other axes. Right now, the cursor is bound to a
certain figure, however this could be changed easily.

#### How to use

To initiate a cursor, just use `Cursor()`.

Blitting enables smooth motion of the cursor (high fps), but can be
deactivated with the option `blit=False` (by default, `blit=True`).

Cursor style can be modified with the options color, style and size, which
correspond to matplotlib's color, linestyle and linewidth respectively.
By default, `color` is red, `style` is dotted (:), `size` is 1.

The cursor can leave marks and/or record click positions if there is a 
click with a specific button (by default, left mouse button). Options:
- `mark_clicks` (bool, False by default)
- `record_clicks` (bool, if True, create a list of click positions)
- `click_button` (1, 2, or 3 for left, middle, right mouse btn, default 1)
- `mark_symbol` (usual matplolib's symbols, default is '+')
- `mark_size` (matplotlib's markersize)
    
Note: currently, the mark color is always the same as the cursor.

##### Example
`Cursor(blit=False, color='b', size=0.5, style='-')`
(this one will be slow because of the blit=False option)
    
#### Interactive Key shortcuts
- Space bar: toggle cursor visitbility (on/off).
- Up/down arrows: increase or decrease size (linewidth).
- Left/right arrows: cycle through different cursor colors.

#### Notes
- Using panning and zooming works with the cursor on; to enable this, 
blitting is temporarily suspended during a click+drag event.
- A small bug is that if I create one or several cursors within main()
they do not show up. Typing Cursor() in the console works, though.
- Cursor is not initiated if the figure has no axes.

### ginput function

Identical to Matplotlib's ginput, except that it uses a cursor.

## Module requirements
- matplotlib
- numpy

## Python requirements
Python : >= 3.6 (because of f-strings)