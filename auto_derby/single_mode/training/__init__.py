from .training import Training
from .partner import Partner
from .globals import g
import logging
from .history import History

# Deprecated: remove at next major version
LOGGER = logging.getLogger(__name__)

__all__ = ["g"]
