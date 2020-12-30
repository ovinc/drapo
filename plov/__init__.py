"""Additional Interactive Features for Matplotlib.

Draggable shapes
- Line is a class that creates a draggable line.
- Rect is a class that creates a draggable rectangle.

Cursor and ginput
- Cursor is a class that creates a cursor that follows the mouse
- ginput is a function based on Cursor that returns data from clicks/keystrokes.

Other
- ClickFig is a class that activates figures and axes (makes them the current
ones) by mouse hovering and clicking.

"""

from .cursor import Cursor
from .cursor import ginput

from .line import Line

from .rectangle import Rect
from .rectangle import rinput

from .clickfig import ClickFig
