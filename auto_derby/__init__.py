from .log import (
    Service as LogService,
    NoOpService as _DefaultLogService,
    Level as LogLevel,
)
from ._config import config
from .plugin import Plugin
from . import services
from .infrastructure.cleanup_service import CleanupService as _DefaultCleanupService

log: LogService = _DefaultLogService()
cleanup: services.Cleanup = _DefaultCleanupService()
