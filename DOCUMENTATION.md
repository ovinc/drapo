# `drapo` detailed documentation

## General notes

- All interactive objects (Line, Rect, Cursor) use blitting (see https://matplotlib.org/3.1.1/api/animation_api.html#funcanimation) for fast rendering. Use the option `blit=False` if this generates display bugs or if using Matplotlib graphical backends (e.g. MacOSX) that have trouble with it.

- The last interactive object instance dictates the blitting behavior (True or False) for every other existing object.

- All interactive objects are subclasses of a base class called *InteractiveObject*. See *DEVELOPMENT.md* for details on code structure, implementation and subclassing.

- By default, all instances are non-blocking. Use `block=True` to make them block the console (not implemented in Line/Rect at the moment). The ginput() function uses the Cursor class in blocking mode.

## Line class

Interactive draggable line in matplotlib figure/axes.

```python
Line(fig=None, ax=None, pickersize=5, color=None, c=None, ptstyle='.', ptsize=5, linestyle='-', linewidth=1, avoid_existing=True, blit=True, block=False, verbose=False)
```

The line is composed of three elements : two points at the edge (pt1, pt2)
and the line between them (link), with customizable appearance.

Dragging the line can be done in two different ways:
- clicking on one edge: then the other edge is fixed during motion
- clicking on the line itself: then the line moves as a whole (do not use this
  mode if the figure/axes have nonlinear scale, e.g. log)

Right-clicking removes and deletes the line.

### Parameters

All parameters optional so that a line can simply be created by `Line()`
without any other specification.

- `fig` (matplotlib figure, default: current figure, specified as None).
- `ax` (matplotlib axes, default: current axes, specified as None).
- `pickersize` (float, default: 5), tolerance for line picking.
- `color` (matplotlib's color, default: None (class default value)).
- `c` (shortcut for `color`)

Appearance of the edge points (pt1, pt2):
- `ptstyle` (matplotlib's marker, default: dot '.').
- `ptsize` (float, default: 5). Marker size.

Appearance of the connecting line (link):
- `linestyle` (matplotlib's linestyle, default: continuous '-').
- `linewidth` (float, default: 1). Line width.

Instantiation option:
- `avoid_existing` (bool, default: True). Avoid overlapping existing lines
(only avoids that edge points overlap, but lines can still cross).

Other
- `blit` (bool, default True). If True, blitting is used for fast rendering
- `block`(bool, default False). If True, object blocks the console (block not implemented yet for Line and Rect).
- `verbose` (bool, default False). If True, some events associated with
            interactive objects are printed in the console.

### Notes

- By default, the line is created on the active figure/axes.
To instantiate a line in other figure/axes, either specify the key/ax
parameters, or use `ClickFig()` to activate these axes.

- When instantiating a line, there is a check to see if any of the edges
overlap with an edge of an existing line. If it's the case, the line is
shifted (up and left) to avoid overlapping. Use `avoid_existing=False` to suppress this behavior.

- If edges of different lines overlap at some point, it is easy to
separate them by clicking on one of the lines, away from the edges, to
drag it away.

- If two lines coincide completely (within pickersize), it is however not
possible to separate them again. Best is to consider them as a single line
and instantiate another line.

- Right-click will simply remove the line, while pressing <kbd>enter</kbd> will save its position in the attribute `self.recorded_position` before erasing the line. This is useful for the *linput()* function.


## Rect class
-------------

Interactive draggable rectangle in matplotlib figure/axes.

```python
Rect(self, fig=None, ax=None, position=None, pickersize=5, color=None, c=None, ptstyle='.', ptsize=5, linestyle='-', linewidth=1, blit=True, block=False, verbose=False, timeout=0):
```

Left click to drag rectangle, right click or enter to remove it. Clicking can be done on the edges, vertices (corners), or on the center. These clicks trigger different modes of motion.

### Parameters

All parameters optional so that a rectangle can be created by `Rect()`.

- `fig` (matplotlib figure, default: current figure, specified as None).
- `ax` (matplotlib axes, default: current axes, specified as None).
- `position` (4-tuple (xmin, ymin, width, height) in data coordinates; default None, i.e. rectangle automatically centered in axes).
- `pickersize` (float, default: 5), tolerance for object picking.
- `color` (matplotlib's color, default: None (class default value)).
- `c` (shortcut for `color`)

Appearance of the vertices (corners):
- `ptstyle` (matplotlib's marker, default: dot '.').
- `ptsize` (float, default: 5). Marker size.

Appearance of the edges (lines):
- `linestyle` (matplotlib's linestyle, default: continuous '-').
- `linewidth` (float, default: 1). Line width.

Other
- `blit` (bool, default True). If True, blitting is used for fast rendering
- `block`(bool, default False). If True, object blocks the console (block not implemented yet for Line and Rect).
- `verbose` (bool, default False). If True, some events associated with
            interactive objects are printed in the console.
- `timeout` (float, default 0, i.e. infinite) timeout for blocking.


### Notes

- Click on the center of the rectangle (marked with a cross) to move the rectangle as a whole in a *solid body* fashion.

- Right-click will simply remove the rectangle, while pressing <kbd>enter</kbd> will save its position in the attribute `self.recorded_position` before erasing the rectangle. This is useful for the *rinput()* function.


## Cursor class
---------------

Cursor following the mouse on any axes of a single figure.

``` python
Cursor(self, fig=None, color=None, c=None, linestyle=':', linewidth=1, horizontal=True, vertical=True, blit=True, visible=True, show_clicks=False, record_clicks=False, mouse_add=1, mouse_pop=3, mouse_stop=2, marker='+', marker_size=None, marker_style='-', n=1000, block=False, timeout=0, verbose=False)
```

This class creates a cursor that moves along with the mouse. It is drawn
only within existing axes, but contrary to the matplotlib widget Cursor,
is not bound to specific axes: moving the mouse over different axes will
plot the cursor in these other axes. Right now, the cursor is bound to a
certain figure, however this could be changed easily.

Cursor style can be modified with the options `color`, `linestyle` and
`linewidth`, which correspond to matplotlib's parameters of the same name.
By default, color is red, linestyle is dotted (:), linewidth is 1.

Cursor appearance can also be changed by specific key strokes:
- space bar to toggle visibility (on/off)
- Alt + up/down arrows: increase or decrease width (linewidth)
- Alt + left/right arrows: cycle through different cursor colors

The cursor can also leave marks and/or record click positions if there is
a click with a specific button (by default, left mouse button). Clicks can
be removed with the remove button (by default, right mouse button), and
stopped with the stop button (by default, middle mouse button).

Addition / removal / stop of clicks are also achieved by key strokes:
- 'a' for addition (corresponds to left click)
- 'z' for removal (corresponds to right click)
- 'enter' for stopping clicks (corresponds to middle click)


### Parameters

All parameters optional so that a cursor can just be created by `Cursor()`
without any other specification.

- `fig` (matplotlib figure, default: current figure, specified as None).
- `color` (matplotlib's color, default: None (class default value)).
- `c` (shortcut for `color`)
- `linestyle` (matplotlib's linestyle, default: dotted ':').
- `linewidth` (float, default: 1.0). Line width.
- `horizontal`: if True (default), display horizontal line of cursor
- `vertical`: if True (default), display vertical line of cursor
- `blit` (bool, default: True). Blitting for performance.
- `show_clicks` (bool, default:False). Mark location of clicks.
- `record_clicks` (bool, default False). Create a list of click positions.
- `visible` (bool, default True). If false, cursor initially not visible.

The 3 following parameters can be 1, 2, 3 (left, middle, right mouse btns).
- `mouse_add` (int, default 1). Adds a (x, y) point by clicking.
- `mouse_pop` (int, default 3). Removes most recently added point.
- `mouse_stop`(int, default 2). Stops click recording. Same as reaching n.

The 3 following parameters customize appearance of click marks when shown.
- `marker` (matplolib's symbol, default: '+')
- `marker_size` (matplotlib's markersize, default: None, see below)
- `marker_style` (matplotlib linestyle, if applicable)

`marker` can be any matplotlib marker (e.g. 'o', 'x', etc.), but also
'hline' (full horizontal line), 'vline' (full vertical line), 'crosshair'
(both vertical and horizontal lines spanning axes). In these last 3
situations, `marker_size` refers to linewidth, and `marker_style` to the
linestyle; `marker_style` does not apply to regular matplotlib markers.

These last parameters are useful for ginput-like functions.
- `n` (int, default 1000). Cursor deactivates after n clicks.
- `block` (bool, default False). Block console until nclicks is reached.
- `verbose` (bool, default False). If True, some events associated with
            interactive objects are printed in the console.
- `timeout` (float, default 0, i.e. infinite) timeout for blocking.

### Useful class methods

- `erase_marks()`: erase click marks on the plot.
- `erase_data()`: reset recorded click data.

The methods `create` and `delete` are used internally within the class and
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

- By default, the cursor is created on the active figure/axes.
To instantiate a cursor in other figure/axes, either specify the key/ax
parameters, or use `ClickFig()` to activate these axes.

- As in matplotlib's ginput, `mouse_add`, `mouse_pop` and `mouse_stop`
have keystroke equivalents, respectively `a`, `z` and `enter`. Only the
last one is the same as matplotlib's ginput, to avoid interactions with
other matplotlib's interactive features (e.g. backspace for "back").

- Currently, the mark color is always the same as the cursor.

- It is not allowed to have more than 1 cursor per figure, to avoid
conflicts between cursors in blitting mode.

- Using panning and zooming works with the cursor on; to enable this,
blitting is temporarily suspended during a click+drag event.

- As a result, the cursor does not reappear immediately after panning or
zooming if blitting is activated, but one needs to move the mouse.


## ginput function
------------------

Improved ginput function (graphical data input) compared to Matplotlib's. In particular, a cursor helps for precise clicking and zooming/panning do not add extra click data.

```python
data = ginput(n=1, timeout=0, show_clicks=True, mouse_add=1, mouse_pop=3, mouse_stop=2, color=None, c=None, linestyle=':', linewidth=1, horizontal=True, vertical=True, marker='+', marker_size=None, marker_style='-', cursor=True, blit=True, ax=None, verbose=False):
```

Key shortcuts and mouse clicks follow the Cursor class behavior, in particular the key shortcuts are `a`, `z`, `enter` (instead of *any key*, *backspace* and *enter*). See Cursor class documentation for more info. All Cursor class interactive features are usable.

### Parameters
Parameters are exactly the same as matplotlib.pyplot.ginput, see
https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ginput.html
with the following additional parameters (see drapo.Cursor):

- `color` / c (default None, i.e. auto)
- `linestyle` (default ':')
- `linewidth` (default 1)
- `horizontal` (default True)
- `vertical` (default True)
- `marker` / `marker_size` / `marker_style` (click marker appearance)
- `cursor` (if False, do not show cursor initially; default True)
- `blit` (bool, default True: use blitting for faster rendering)
- `ax` (default None, i.e. last active axes)
- `verbose` (bool, default False). If True, some events associated with
            interactive objects are printed in the console.

### Returns
List of tuples corresponding to the list of clicked (x, y) coordinates.


## linput function
------------------

Select position of line edges on figure with interactive line (enter to validate).

```python
position = linput():   # (x1, y1), (x2, y2)
```

### Parameters

Same as drapo.Line(), but `block` remains always True by default.


### Returns

Tuple of tuples ((x1, y1), (x2, y2)) of data coordinates (unordered).


## rinput function
------------------

Select area of figure with interactive rectangle (enter to validate).

```python
position = rinput():  # (x, y, w, h)
```

### Parameters

Same as `Rect()` except that `block` is automatically set to `True`.

### Returns
4-tuple (xmin, ymin, width, height) of data coordinates.


## ClickFig class
-----------------

Mouse that activates figures and axes by hovering and clicking.

```python
ClickFig(n=-1, highlight=True)
```

- Left Click on figure / axes to make them the current ones in Matplotlib.
- Right Click anywhere to deactivate the interactive mouse.

Use `ClickFig()` to make the interactive mouse active, and select active axes
at will while still working on them. Use `ClickFig(highlight=False)` to not
see background color change during hovering.

For just one-time selection, use `ClickFig()`. The background colors
return to their original values once the ClickFig is deactivated (here,
after one click).

To be able to select n times, use `ClickFig(n)`. Note that it is only the
last axes clicked that are activated.

### Parameters

- n (int, default 1): maximum number of clicks allowed.
- highlight (bool, default True): change ax/fig color when mouse on them.


## Examples
-----------

For the simplest quick-start examples, see *README.md*. The ones below show some more detailed features compared to basic use.

```python
from drapo import Line, Cursor, ClickFig, ginput
```
for the initial import.

```python
Line(color='r', ptstyle='+', ptsize=10, linestyle=':', linewidth=2):
```
creates a thick red, dotted draggable line, with edges drawn as large crosses.

```python
C = Cursor(record_clicks=True, show_clicks=True, nclicks=5)
```
creates a cursor that leaves a red cross at the points clicked and saves the
corresponding position (x, y) data in a list, accessible with `C.clickdata`.
The cursor is deactivated after 5 clicks, but the marks stay on the figure.
To remove the marks, use the `erase_marks()` method. Note that for recording
click positions, it is preferable to use the dedicated `ginput` function.

```python
Cursor(blit=False, color='b', size=0.5, style='-')
```
creates a thin blue cursor with continuous lines; it will be slower
because of the `blit=False` option. The cursor can be thickened by using the
up arrow and changed color by using the left/right arrows.

```python
data = ginput(4, show_clicks=False)
```
will return a tuple of 4 points clicked on the figure (or managed with keystrokes), but without showing the location of the clicks on the figure with a marker.

```python
position = linput()
```
will instantiate an interactive line on the figure. Press enter to deactivate the line and return its position as a tuple ((x1, y1), (x2, y2)) in data coordinates.


```python
position = rinput()
```
will instantiate an interactive rectangle on the figure. Press enter to deactivate the rectangle and return its coordinates as a tuple (xmin, ymin, width, height) in data coordinates.

```python
ClickFig(4)
```
will produce an interactive mouse that highlights the figure/axes it is on,
and allow 4 left-clicks to activate these fig/axes in matplotlib.

```python
ClickFig(-1)
```
does the same, but is active forever. Deactivate it with right-click.