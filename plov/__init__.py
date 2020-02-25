"""Additional Interactive Features for Matplotlib.

*Cursor* is a class that creates a cursor that follows the mouse.

Based on the Cursor class are the following functions:
- `ginput` the same as matplotlib's ginput, but with a cursor.
- `hinput` is ginput (with cursor) but also with zooming/panning abilities.

*Line* is a class that creates a draggable line.
"""

from .cursor import Cursor
from .cursor import ginput
from .cursor import hinput
from .line import Line

__version__ = 0.8