# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false

from __future__ import annotations

import warnings

from .null_device_service import NullDeviceService as _NullDeviceService

warnings.warn("renamed to null_device_service", DeprecationWarning)

globals()["NoOpDeviceService"] = _NullDeviceService
