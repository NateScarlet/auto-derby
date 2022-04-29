# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import socket


import auto_derby
from auto_derby.infrastructure.web_log_service import WebLogService


class Plugin(auto_derby.Plugin):
    """make web log public visible"""

    def install(self) -> None:
        WebLogService.default_host = socket.gethostname()


auto_derby.plugin.register(__name__, Plugin())
