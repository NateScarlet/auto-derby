from .log import (
    Service as LogService,
    NoOpService as _DefaultLogService,
    Level as LogLevel,
)
from ._config import config
from .plugin import Plugin


log: LogService = _DefaultLogService()
