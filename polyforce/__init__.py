__version__ = "0.1.0"

from .config import Config
from .decorator import polycheck
from .main import PolyModel

__all__ = ["Config", "polycheck", "PolyModel"]
