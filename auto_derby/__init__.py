from . import services
from ._config import config
from .infrastructure.cleanup_service import CleanupService as _DefaultCleanupService
from .infrastructure.no_op_log_service import NoOpService as _DefaultLogService
from .plugin import Plugin
from .services.log import Level as LogLevel

log: services.Log = _DefaultLogService()
cleanup: services.Cleanup = _DefaultCleanupService()
