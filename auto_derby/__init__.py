from .log import Service, NoOpService as _DefaultLogService, Level as LogLevel
from ._config import config
from .plugin import Plugin


log: Service = _DefaultLogService()
