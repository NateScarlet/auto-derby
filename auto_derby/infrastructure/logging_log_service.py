# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import logging
from typing import Text

from ..log import NoOpLogService


class LoggingLogService(NoOpLogService):
    def __init__(self, logger: logging.Logger) -> None:
        self._l = logger

    def debug(self, msg: Text, /):
        self._l.debug(msg)

    def info(self, msg: Text, /):
        self._l.info(msg)

    def warn(self, msg: Text, /):
        self._l.warn(msg)

    def error(self, msg: Text, /):
        self._l.error(msg)

    def image_url(self, caption: Text, url: Text, /):
        self._l.info("![%s](%s)", caption, url)
