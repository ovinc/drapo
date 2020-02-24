# Plot-OV (plov) - Additional interactive Matplotlib features

## General information on contents

*Cursor* is a class that creates a cursor that follows the mouse.

Based on the Cursor class are the following functions:
- `ginput` the same as matplotlib's ginput, but with a cursor.
- `hinput` is ginput (with cursor) but also with zooming/panning abilities.

*Line* is a class that creates a draggable line.

## Documentation

### Line class

```python
Line(position=(0.2, 0.2, 0.8, 0.8), fig=None, ax=None, pickersize=5)
```

Two dots connected by a line, draggable by its ends (the dots)
    
- Creates a draggable line on a matplotlib figure/axes.
- Right-click to remove line.
- If mouse leaves axes, control over the line is lost.

To initiate a line, just use `Line()`.

### Cursor class

Cursor following the mouse on any axes of a single figure.

``` python
Cursor(fig=None, color='r', style=':', size=1, blit=True,
        show_clicks=False, record_clicks=False,
        mouse_add=1, mouse_pop=3, mouse_stop=2,
        n=1000, block=False, timeout=0, 
        mark_symbol='+', mark_size=10)
```

This class creates a cursor that moves along with the mouse. It is drawn
only within existing axes, but contrary to the matplotlib widget Cursor,
is not bound to specific axes: moving the mouse over different axes will
plot the cursor in these other axes. Right now, the cursor is bound to a
certain figure, however this could be changed easily.

Cursor style can be modified with the options `color`, `style` and `width`,
which correspond to matplotlib's color, linestyle and linewidth respectively.
By default, color is red, style is dotted (:), width is 1.

Cursor apparance can also be changed by specific key strokes:
- space bar to toggle visibility (on/off)
- up/down arrows: increase or decrease width (linewidth)
- left/right arrows: cycle through different cursor colors.

The cursor can also leave marks and/or record click positions if there is 
a click with a specific button (by default, left mouse button). Clicks can
be removed with the remove button (by default, right mouse button), and
stopped with the stop button (by default, middle mouse button).

Addition / removal / stop of clicks are also achieved by key strokes:
- `a` for addition (corresponds to left click)
- `z` for removal (corresponds to right click)
- `enter` for stopping clicks (corresponds to middle click).
    
### Parameters

All parameters optional so that a cursor can be created by `Cursor()`.

- `fig` (matplotlib figure, default: current figure, specified as None).
- `color` (matplotlib's color, default: red, i.e. 'r').
- `style` (matplotlib's linestyle, default: dotted ':').
- `width` (float, default: 1.0). Line width.
- `blit` (bool, default: True). Blitting for performance.
- `show_clicks` (bool, default:False). Mark location of clicks.
- `record_clicks` (bool, default False). Create a list of click positions.

The 3 following parameters can be 1, 2, 3 (left, middle, right mouse btns).
- `mouse_add` (int, default 1). 
- `mouse_pop` (int, default 3). Removes most recently added point.
- `mouse_stop`(int, default 2). Stops click recording. Same as reaching n.

The 3 following parameters are useful for ginput-like functions.
- `n` (int, default 1000). Cursor deactivates after n clicks.
- `block` (bool, default False). Block console until nclicks is reached.
- `timeout` (float, default 0, i.e. infinite) timeout for blocking.

The last 2 parameters customize appearance of click marks when shown.
- `mark_symbol` (matplolib's symbol, default: '+')
- `mark_size` (matplotlib's markersize, default 10)


### Useful class methods

- `erase_marks()`: erase click marks on the plot. 
- `erase_data()`: reset recorded click data.

The methods `create` and `erase` are used internally within the class and
are not meant for the user.

### Useful class attributes

- `fig`: matplotlib figure the cursor is active in. Fixed.
- `ax`: matplotlib axes the cursor is active in. Changes in subplots.
- `visibility`: bool, sets whether cursor drawn or not when in axes.
- `inaxes`: book, true when mouse (and thus cursor) is in axes
- `clicknumber`: track the number of recorded clicks.
- `clickdata`: stores the (x, y) data of clicks in a list.
- `marks`: list of matplotlib artists containing all click marks drawn.
    
### Notes

- As in matplotlib's ginput, `mouse_add`, `mouse_pop` and `mouse_stop`
have keystroke equivalents, respectively `a`, `z` and `enter`. Only the
last one is the same as matplotlib's ginput, to avoid interactions with
other matplotlib's interactive features (e.g. backspace for "back").
- Currently, the mark color is always the same as the cursor.
- It is not allowed to have more than 1 cursor per figure, to avoid 
conflics between cursors in blitting mode.
- Using panning and zooming works with the cursor on; to enable this,
blitting is temporarily suspended during a click+drag event.
- As a result, the cursor does not reappear immediately after panning or
zooming if blitting is activated, but one needs to move the mouse.


## ginput function

Identical to matplotlib's ginput, with added cursor for easier clicking.

```python
data = ginput(*args, **kwargs)
```

Key shortcuts and mouse clicks follow matplotlib's behavior. The Cursor 
class only acts on the cursor here (appearance, with key Cursor class 
associated key shortcuts), not on the clicking and data recording which
follow matplotlib ginput. See matplotlib.pyplot.ginput for help. 

## hinput function

Similar to ginput, but zooming/panning does not add extra click data.

```python
data = hinput(n=1, timeout=0, show_clicks=True,
           mouse_add=1, mouse_pop=3, mouse_stop=2,
           blit=True):
```

Here, contrary to ginput, key shortcuts and mouse clicks follow the
plov Cursor class behavior, in particular the key shortcuts are
`a`, `z`, `enter` instead of any key, backspace and enter. See 
Cursor class documentation for more info. All Cursor class interactive
features are usable.

### Parameters

Parameters are exactly the same as matplotlib.pyplot.ginput, with only an
additional one: blit (bool, default True): blitting for performance.

### Returns

List of tuples corresponding to the list of clicked (x, y) coordinates.


## Examples
```python
C = Cursor(record_clicks=True, show_clicks=True, nclicks=5)
```
creates a cursor that leaves a red cross at the points clicked and saves the
corresponding position (x, y) data in a list, accessible with `C.clickdata`.
The cursor is deactivated after 5 clicks, but the marks stay on the figure.
To remove the marks, use the `erase_marks()` method.

```python
Cursor(blit=False, color='b', size=0.5, style='-')
```
creates a thin blue cursor with continuous lines; it will be slower
because of the blit=False option. The cursor can be thickened by using the
up arrow and changed color by using the left/right arrows.

```python
hinput(4)
```
will return 4 points clicked on the figure (or managed with keystrokes)
    

## Module requirements
- matplotlib
- numpy

## Python requirements
Python : >= 3.6 (because of f-strings)

## Author
Olivier Vincent, 2019-2020.