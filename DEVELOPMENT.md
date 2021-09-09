# Development information for *drapo*

All drapo classes except ClickFig (not described here) use a **base class** named **InteractiveObject** located in the file *interactive_object.py*. The base class is mainly developed for objects that are set in motion when they are selected (picked) by a click, and moved by dragging the object while keeping the mouse pressed, like the **Line** and **Rect** classes. These classes, as a result, use most of the base class methods with little modification. The **Cursor** class has a behavior slightly different where the object moves spontaneously with the mouse without a click. As a result, it has to redefine more of the base class methods. The base class allows for all those objects to be managed in the same framework and thus enables dragging of several objects (possibly of different types) at the same time, and efficient rendering of the motion of these objects through a globally set blitting mode.


## General structure
- Events on a Matplotlib figure (click, mouse motion, key press, enter axes, etc.) are tied to *callback functions* through Matplotlib's event handling manager (see https://matplotlib.org/users/event_handling.html). The base class manages these events with the `connect()` and `disconnect()` methods.

- Callback functions (`on_mouse_press`, `on_motion`, etc.) can be redefined in subclasses if necessary. In the base class, they are optimized for click-enabled draggable objects like Line and Rect. These callback functions call methods that are either base class methods or specific class methods (see below). For example, motion of draggable objects is triggered by a picking event (callback `on_pick`) and is then managed by the callback function `on_motion`. **Cursor** redefines the adequate methods to fit its different behavior.

- During motion, blitting is used for fast rendering. The principle is to save non-moving objects as a background pixel image and just re-draw moving objects on it. If blitting is deactivated with the `blit=False` option, all contents on the figure is re-drawn at every step, which is much slower and results in lag. The `cls.blit` bool attribute is managed by the base class and common to all subclasses, so that the last instance of any class defines whether blitting is used or not for all objects present.

- Because several objects can be moving at the same time (e.g. two lines dragged by the same click), display and blitting can be tricky and buggy. To solve this problem, one of the moving objects is defined as the leader. The leader object is stored in the `cls.leader` attribute of the base class, which is thus common to all subclasses. Only the leader calls graph update events, during which all other moving objects (stored in another class attribute `cls.moving_objects`) are updated at the same time.

- The tasks above are managed by `initiate_motion` (define leader) and `update_graph` (synchronized animation and blitting), two base class methods that call specific class methods when needed (see below); `reset_after_motion` is called at the end of motion (typically on mouse release) to reset everything properly. Once again, the Cursor class manages things a bit differently but uses the same `update_graph` method.


## Base class

The methods and attributes below are common to all subclasses through the base class

### Instance methods

- **update_graph(event)** manages the motion of objects in the figure and should only be called by the `cls.leader` object (defined in `initiate_motion`, see below); other objects are drawn with a loop on all `moving_objects`. In subclasses, `update_graph` is typically called in the `on_motion` callback.

- **initiate motion(event)** needs to be called before `update_graph` to define the leading object, define animated artists on the figure, and store other useful info for motion. In particular, it calls the `set_active_info` method that needs to be defined in the subclass, as well as the `set_press_info` and `set_motion_tracking` methods which are defined in the base class. An exception is for cursors, which are always moving by default, and which deactivate during the motion of other objects (lines, rectangles, etc.). Cursor objects, as a result, are never defined as leaders. `initiate motion` needs to be called in the subclass by another method or callback (typically `on_pick` or `on_press`) that itself already defines which objects will be moving (by adding them to `moving_objects`). Cursor does not use this method.

- **set_press_info(event)**: generate information about a click event, i.e. its position and the position the object's elements (tracked points) relative to it, all stored in the dictionary `self.press_info`. It also defines the attribute `self.moving_positions`, which is a dictionary that store positions of tracked points during motion. For it to work, the attribute `all_pts` needs to be defined by the subclass `create` method. Cursor overwrites this method.

- **reset_after_motion()** basically reverses `initiate_motion` and other parameters.

- **delete()** and **erase()** cancel `create()` (which has to be defined in the subclasses, see below), temporarily for `erase` and permanently for `delete`.

- **delete_others(option)** applies `delete` to all other members of the same class, except `self`. Useful to have only one type of object on the figure (e.g. for cursors). Can be applied to all objects of the same class (`option='all'` or by simply calling `delete_others()`), all class objects in the same figure (option=`'fig'`), or all class objects in the same axes (`option='ax'`).

- **get_pt_position(pt, option)** returns the position x, y (tuple) of a matplotlib single point from the matplotlib.lines.Line2D data, either as data coordinate tied to axes (`option='data'`, default), or as absolute pixel coordinates in the figure (`option='px'`)

- **create()**, **update_position()** and **set_active_info()** need to be defined in the subclasses with some specific constraints, see below.

- **connect()**, **disconnect()** manage the Matplotlib figure event manager, and ***callbacks*** are optimized for draggable objects,  see above.


### Class methods

- **class_objects()**: returns all instances of a given class, excluding parent/children class.
- **all_objects()**: returns all interactive objects, including parent/children/siblings etc.
- **clear()**: removes all interactive objects.

### Class attributes

- **name**: should be also defined for every subclass, as it is used by the default `__repr__` and `__str__` defined in the base class.

- **all_interactives_objects**: stores all interactive objects of any class within ***drapo***. Objects are appended to this list during the init of the base class, so there is no need to do anything in the subclasses. In fact, subclasses *should not* define a class attribute with the same name. This attribute is the list returned when calling `cls.all_objects()`.

- **moving_objects**: stores all objects (of any class) that need to be updated when calling `update_graph`. Objects are added to this set by `self.initiate_motion()` and removed from this set by `self.reset_after_motion()`. If not using these two initiate/reset methods, the subclass should manage addition and removal to `moving_objects`.

- **leader**: instance of any subclass that is the leading object for synchronized graph updating (see above). It is defined in `initiate_motion`, which blocks any other object to be defined as the leader until the leader is reset to `None`, e.g. when calling `reset_after_motion`.

- *Blitting* attributes: **blit** (bool, general blitting behavior, is defined by the last instance to be created), **background** (the pixel background currently used for blitting), **initiating_motion** (bool, will trigger background save for blitting in `update_graph` if True).

- **colors**: default class line colors, that are cycled through if necessary.


## Subclassing

### Subclass instance methods

The methods below are present in the base class but are (mostly) empty. They need to be redefined in each subclass to fit the needs of that specific class.

- **create()**: create the object. The minimal thing it needs to do is define the `all_artists` attribute, which is a list of all Matplotlib artists the object is made of, and `all_pts` which is a list of the points (Line2D artists with a single (x, y) coordinate) that need to be tracked during motion (typically, all points composing the object). Apart from this, its structure (number of arguments etc.) can be adapted for the needs of every subclass.

- **update_position(event)** is called by `update_graph` to define how an object of every specific class needs to be updated following the position of the mouse (mouse event `event`).

- **set_active_info**: generate information about the active object, e.g. its mode of motion and which parts of it need to be updated during motion, stored in the dictionary `self.active_info`.

### Callbacks

- if overriding the `on_resize` callback, make sure to include the original commands to redefine `postodata` and `datatopos` that provide transforms between data coordinates and pixel coordinates in the figure/axes.

### Subclassing requirements

To summarize the information above, subclasses need to do the following things:

- define local `cls.name`,
- *do not* define local `cls.all_interactive_objects`, `cls.moving_objects`, `cls.leader`, `cls.initiating_motion`, `cls.blit`, `cls.background` so that when these values are called or updated, they are shared with the parent and sibling classes,
- *do not* append instance to global `cls.all_interactive_objects` (taken care of by the base class),
- redefine locally the `self.create`, `self.update_position`, `self.set_active_info` methods,
- make sure `self.create` defines `all_artists` and `all_pts`,
- make sure to keep `postodata` and `datatopos` definitions in the `on_resize` callback,
- In the adequate callbacks:
    + call `self.initiate_motion` (global) to define leader, or check existing leader before motion,
    + call `self.update_graph` (global) to create animation during motion or to trigger object update; during motion, make sure that only the leading object calls the method,
    + call `self.reset_after_motion` after motion is done to reset things like leader, background, moving_objects and other info.
    + if not using the initiate/reset methods described above, make sure the subclass manages addition and removal to `cls.moving_objects`.


# Testing

## Testing interactive objects

Testing is done with *pytest*. Simply `cd` into the root of the module and run
```bash
pytest
```
This will open several windows with interactive objects one can interact with. To see the various interactive tests one can do with the objects, see below.

(Note: the test uses the *Qt5Agg* backend by default and switches to *TkAgg* if the first one is not available).

One can also run the demo (backend and blitting options available):
```bash
python -m drapo.demo
python -m drapo.demo --backend TkAgg
python -m drapo.demo --blit False
```

## Recommended tests with objects

Verify that ...

### Line

- Dragging works on all axes, in both dragging modes (by clicking on line ends or by clicking on the line itself).
- Dragging two lines or more at the same time works in both modes.
- Use matplotlib's zooming and panning tool on axes with lines. Check in particular that when finishing the zoom, moving the mouse again without zooming activated does not produce blitting bugs.
- Make the mouse exit and re-enter the axes and figures and check for display bugs.


### Rect

Testing follows the same procedure as with the Line class. Also try dragging a rectangle and other objects (lines) separately or at the same time.

Specific things to test for rectangles:
- Dragging the rectangle "over itself" by making the lines cross should not be problematic.
- Center point should always be in the center of the rectangle, even in nonlinear axes.


### Cursor

- Check that the cursor is automatically created when mouse enters any of the subplots.
- While cursor is on, press Alt+(up/down/left/right) to change thickness and color. Changes should be immediately effective and appear without any other action needed.
- Press space to deactivate/reactivate cursor. Deactivate it outside of the figure as well and check that it does not appear when the mouse comes back in the axes.
- Check interaction with Line and Rect instances.


## Other development tests

The tests below are not done with pytest but are other recommended tests.

### ginput function

(can be partially done while running the demo, see above)

- Verify that left click adds a red cross at the location of the click and that left click anywhere removes the cross.
- Same for 'a' and 'z' keystrokes.
- Verify that recording stops after the fourth cross has been added and that a list of 4 tuples is returned in the console.
- Re-instanciate a ginput Cursor with `drapo.cursor.main()` and check that recording can be interrupted by pressing the "enter" key, and that a list of tuples shorter than 5 is returned.

### Line

Additional tests:

- Instantiate a cursor with `Cursor()`, and do the same as above with the cursor on. Cursor should disappear when lines are dragged.
- Instantiate another line with `l = Line()` and check that `l.all_objects()` and `l.class_objects()` return correct information (*all_objects* should include the cursor, *class_objects* should include only lines; also check that the display name of the lines in the list is consistent in an interactive python window).
- Test the class method `l.delete_others()` with arguments *'ax'*, *'fig'*, and no argument to see the other lines in the same axes, figure, and all other lines being progressively removed from all_objects and class_objects.

### Clickfig class

To test the ClickFig class, run
```python
drapo.clickfig.main()
```
which runs ClickFig with one click allowed; check that hovering the mouse over different figure/axes highlights them in light blue. Click on one of them, then run `plt.plot(1, 2, 'or')` in the console to check that it plots the result in the selected axes.


### All classes

For all classes, it is useful to also check the following things :
- Re-run tests by passing the argument `blit=False` in main() to see if things still work without blitting.
- Re-run basic tests with other Matplotlib backends: pass the argument `backend='yyy'` where *yyy* is the name of the backend (try e.g. *Qt5Agg*, *Qt4Agg*, *TkAgg*)
