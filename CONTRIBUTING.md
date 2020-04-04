# Development information for Plot-OV (plov)


All Plot-OV (plov) classes use a **base class** named **InteractiveObject** located in the file *interactive_object.py*. The only exception is **ClickFig**, which works differently and is on its own and will not be described here.

## General structure

- Events on a Matplotlib figure (click, mouse motion, key press, enter axes, etc.) are tied to *callback functions* through Matplotlib's event handling manager (see https://matplotlib.org/users/event_handling.html). The base class manages these events with the `connect()` and `disconnect()` methods. Event data is passed to callbacks with the `event` parameter.

- Callback functions (`on_mouse_press`, `on_motion`, etc.) are defined, but mostly empty in the base class, and those needed have to be defined in subclasses.

- These callback functions call methods that are either base class methods or specific class methods (see below).

- Motion of objects is typically triggered by a picking event (callback `on_pick`) or mouse press event (callback `on_mouse_press`) and is then managed by the callback function `on_motion`. **Cursor** works a little differently: it is always moving by default and deactivates when the mouse is pressed, to avoid display bugs that appear when zooming/panning in blitting mode.

- During motion, blitting is used for fast rendering. The principle is to save non-moving objects as a background pixel image and just re-draw moving objects on it. If blitting is deactivated with the `blit = False` option, all contents on the figure is re-drawn at every step, which is much slower and results in lag. The `cls.blit` bool attribute is managed by the base class and common to all subclasses, so that the last instance of any class defines whether blitting is used or not for all objects present.

- Because several objects can be moving at the same time (e.g. two lines dragged by the same click), display and blitting can be tricky and buggy. To solve this problem, one of the moving objects is defined as the leader. The leader object is stored in the `cls.leader` attribute of the base class, which is thus common to all subclasses. Only the leader calls graph update events, during which all other moving objects (stored in another class attribute `cls.moving_objects`) are updated at the same time.

- The tasks above are managed by `initiate_motion` (define leader) and `update_graph` (synchronized animation and blitting), two base class methods that call specific class methods when needed (see below); `reset_after_motion` is called at the end of motion (typically on mouse release) to reset everything properly.


## Base class

The methods and attributes below are common to all subclasses through the base class

### Instance methods
    
- **update_graph(event)** manages the motion of objects in the figure and should only be called by the `cls.leader` object (defined in `initiate_motion`, see below); other objects are drawn with a loop on all `moving_objects`. In subclasses, `update_graph` is typically called in the `on_motion` callback. 

- **initiate motion(event)** needs to be called before `update_graph` to define the leading object, define animated artists on the figure, and store other useful info for motion. In particular, it calls the `set_press_info` and `set_active_info` methods that need to be defined in the subclass. An exception is for cursors, which are always moving by default, and which deactivate during the motion of other objects (lines, rectangles, etc.). Cursor objects, as a result, are never defined as leaders. `initiate motion` needs to be called in the subclass by another method or callback (typically `on_pick` or `on_press`) that itself already defines which objects will be moving (by adding them to `moving_objects`).

- **reset_after_motion()** basically reverses `initiate_motion` and other parameters.

- **delete()** and **erase()** cancel `create()` (which has to be defined in the subclasses, see below), temporarily for `erase` and permanently for `delete`.

- **delete_others(option)** applies `delete` to all other members of the same class, except `self`. Useful to have only one type of object on the figure (e.g. for cursors). Can be applied to all objects of the same class (`option='all'` or by simply calling `delete_others()`), all class objects in the same figure (option=`'fig'`), or all class objects in the same axes (`option='ax'`).

- **get_pt_position(pt, option)** returns the position x, y (tuple) of a matplotlib single point from the matplotlib.lines.Line2D data, either as data coordinate tied to axes (`option='data'`, default), or as absolute pixel coordinates in the figure (`option='px'`)

- **connect()**, **disconnect()**, and ***callbacks***: see above.

### Class methods

- **class_objects()**: returns all instances of a given class, excluding parent/children class.
- **all_objects()**: returns all interactive objects, including parent/children/siblings etc.
- **clear()**: removes all interactive objects.

### Class attributes

- **name**: should be also defined for every subclass, as it is used by the default `__repr__` and `__str__` defined in the base class.

- **all_interactives_objects**: stores all interactive objects of any class within ***plov***. Objects are appended to this list during the init of the base class, so there is no need to do anything in the subclasses. In fact, subclasses *should not* define a class attribute with the same name. This attribute is the list returned when calling `cls.all_objects()`. 
 
- **moving_objects**: stores all objects (of any class) that need to be updated when calling `update_graph`. Objects are added to this set by `self.initiate_motion()` and removed from this set by `self.reset_after_motion()`. If not using these two initiate/reset methods, the subclass should manage addition and removal to `moving_objects`.

- **leader**: instance of any subclass that is the leading object for synchronized graph updating (see above). It is defined in `initiate_motion`, which blocks any other object to be defined as the leader until the leader is reset to `None`, e.g. when calling `reset_after_motion`.

- *Blitting* attributes: **blit** (bool, general blitting behavior, is defined by the last instance to be created), **background** (the pixel background currently used for blitting), **initiating_motion** (bool, will trigger background save for blitting in `update_graph` if True).

- **colors**: default class line colors, that are cycled through if necessary.


## Subclassing

### Subclass instance methods

The methods below are present in the base class but are (mostly) empty. They need to be redefined in each subclass to fit the needs of that specific class.

- **create()**: create the object. The minimal thing it needs to do is define the `all_artists` attribute, which is a list of all Matplotlib artists the object is made of. Apart from this, its structure (number of arguments etc.) can be adapted for the needs of every subclass.

- **update_position(event)** is called by `update_graph` to define how object of every specific class needs to be updated following the position of the mouse (mouse event `event`).

- **set_active_info**: generate information about the active object, e. g. its mode of motion and which parts of it need to be updated during motion, stored (either directly in the method or as a return of the method) in the dictionary `self.active_info`.

- **set_press_info**: generate information about the click, e. g. its position and the position the object relative to it, stored (either directly in the method or as a return of the method) in the dictionary `self.press_info`.

### Callbacks

- if overriding the `on_resize` callback, make sure to include the original commands to redefine `postodata` and `datatopos` that provide transforms between data coordinates and pixel coordinates in the figure/axes.

### Subclassing requirements

To summarize the information above, subclasses need to do the following things:

- define local `cls.name`,
- *do not* define local `cls.all_interactive_objects`, `cls.moving_objects`, `cls.leader`, `cls.initiating_motion`, `cls.blit`, `cls.background` so that when these values are called or updated, they are shared with the parent and sibling classes,
- *do not* append instance to global `cls.all_interactive_objects` (taken care of by the base class),
- redefine locally the `self.create`, `self.update_position`, `self.set_active_info`, `self.set_press_info` methods,
- define locally the callback functions and make them call the class methods,
- make sure to keep `postodata` and `datatopos` definitions in `on_resize`,
- call `self.initiate_motion` (global) to define leader or check existing leader before motion,
- call `self.update_graph` (global) to create animation during motion or to trigger object update; for motion, make sure that only the leading object calls the method,
- call `self.reset_after_motion` after motion is done to reset things like leader, background, moving_objects and other info.
- if not using the initiate/reset method, make sure the subclass manages addition and removal to `cls.moving_objects`.


## Testing

After modifying code, do at least the following tests to check that the package is still working properly. Start by importing the package. In a python shell, run
```python
import plov
```

### Base class

To test the base class IneractiveObject, run
```python
plov.interactive_object.main()
```

A blank matplotlib window should open. When clicking or pressing keys on the figure, information on the clicks / keys should be printed in the shell.

### Line class

To test the Line class, run
```python
plov.line.main()
```
This will instantiate various lines on different axes of two figures, with linerar and log scales. Verify the following:
- Dragging works on all axes, in both dragging modes (by clicking on line ends or by clicking on the line itself).
- Dragging two lines or more at the same time works in both modes.
- Use matplotlib's zooming and panning tool on axes with lines. Check in particular that when finishing the zoom, moving the mouse again without zooming activated does not produce blitting bugs.
- Make the mouse exit and re-enter the axes and figures and check for display bugs.
- Instantiate a cursor with `Cursor()`, and do the same as above with the cursor on. Cursor should disappear when lines are dragged.
- Instantiate another line with `l = Line()` and check that `l.all_objects()` and `l.class_objects()` return correct information (*all_objects* should include the cursor, *class_objects* should include only lines; also check that the display name of the lines in the list is consistent in an interactive python window).
- Test the class method `l.delete_others()` with arguments *'ax'*, *'fig'*, and no argument to see the other lines in the same axes, figure, and all other lines being progressively removed from all_objects and class_objects.

### Rect class
To test the Line class, run
```python
plov.rectangle.main()
```
Testing follows the same procedure as with the Line class. Also try instantiating lines and rectangles in the same axes and drag them separately or at the same time.

### Cursor class and ginput
To test the Cursor class, run
```python
plov.cursor.main()
```
This will open a figure with two subplots, and with a cursor instantiated by the ginput function, aiming at recording 5 data points from the figure.

Testing follows the same procedure as with the Line/Rect classes, with some other specificities to test:

#### Cursor behavior
- Check that the cursor is automatically created when mouse enters any of the subplots.
- While cursor is on, press shift+up/down/left/right to change thickness and color. Changes should be immediately effective and appear without any other action needed.
- Press space to deactivate/reactivate cursor. Deactivate it outside of the figure as well and check that it does not appear when the mouse comes back in the axes.
- Check interaction with Line and Rect instances as is done in the Line procedure.

#### ginput behavior
- Verify that left click adds a red cross at the location of the click and that left click anywhere removes the cross.
- Same for 'a' and 'z' keystrokes.
- Verify that recording stops after the fifth cross has been added and that a list of 5 tuples is returned in the console.
- Re-instanciate a ginput Cursor with `plov.cursor.main()` and check that recording can be interrupted by pressing the "enter" key, and that a list of tuples shorter than 5 is returned.

### Clickfig class
To test the ClickFig class, run
```python
plov.clickfig.main()
```
which runs ClickFig with one click allowed; check that hovering the mouse over different figure/axes highlights them in light blue. Click on one of them, then run `plt.plot(1, 2, 'or')` in the console to check that it plots the result in the selected axes.

### All classes

For all classes, it is useful to also check the following things : 
- Re-run tests by passing the argument `blit=False` in main() to see if things still work without blitting.
- Re-run basic tests with other Matplotlib backends: pass the argument `backend='yyy'` where *yyy* is the name of the backend (try e.g. *Qt5Agg*, *Qt4Agg*, *TkAgg*)


## Contributors

- Olivier Vincent (olivier.a-vincent@wanadoo.fr)
