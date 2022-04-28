from .log import LogService, NoOpLogService as _DefaultLogService
from ._config import config
from .plugin import Plugin


log: LogService = _DefaultLogService()
