# -*- coding=UTF-8 -*-
# pyright: strict
"""application wide dependencies."""

from __future__ import annotations

from .infrastructure.cleanup_service import CleanupService as _DefaultCleanupService
from .infrastructure.no_op_log_service import NoOpService as _DefaultLogService
from .services.log import Level as LogLevel, Service as LogService
from .services.cleanup import Service as CleanupService


DEBUG = LogLevel.DEBUG
INFO = LogLevel.INFO
WARN = LogLevel.WARN
ERROR = LogLevel.ERROR

log: LogService = _DefaultLogService()
cleanup: CleanupService = _DefaultCleanupService()
