# -*- coding=UTF-8 -*-
# pyright: strict
"""application wide dependencies."""

from __future__ import annotations

from .infrastructure.cleanup_service import CleanupService as _DefaultCleanupService
from .infrastructure.null_log_service import NullLogService as _DefaultLogService
from .infrastructure.null_device_service import (
    NullDeviceService as _DefaultDeviceService,
)
from .services.log import Level as LogLevel, Service as LogService
from .services.cleanup import Service as CleanupService
from .services.device import Service as DeviceService, Image, Rect

DEBUG = LogLevel.DEBUG
INFO = LogLevel.INFO
WARN = LogLevel.WARN
ERROR = LogLevel.ERROR
Image = Image
Rect = Rect

log: LogService = _DefaultLogService()
cleanup: CleanupService = _DefaultCleanupService()
device: DeviceService = _DefaultDeviceService()
