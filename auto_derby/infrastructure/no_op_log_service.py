# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false

from __future__ import annotations

import warnings

from .null_log_service import NullLogService as _NullLogService

warnings.warn("renamed to null_log_service", DeprecationWarning)

globals()["NoOpService"] = _NullLogService
