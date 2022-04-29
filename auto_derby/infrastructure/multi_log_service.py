# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Sequence, Text

from auto_derby.log import Image, LogService


class MultiLogService(LogService):
    @classmethod
    def _iter(cls, *services: LogService):
        for i in services:
            if isinstance(i, cls):
                yield from i._s
            else:
                yield i

    def __init__(self, *services: LogService) -> None:
        self._s: Sequence[LogService] = tuple(self._iter(*services))

    def debug(self, msg: Text, /):
        for i in self._s:
            i.debug(msg)

    def info(self, msg: Text, /):
        for i in self._s:
            i.info(msg)

    def warn(self, msg: Text, /):
        for i in self._s:
            i.warn(msg)

    def error(self, msg: Text, /):
        for i in self._s:
            i.error(msg)

    def image(self, caption: Text, image: Image):
        for i in self._s:
            i.image(caption, image)

    def image_url(self, caption: Text, url: Text, /):
        for i in self._s:
            i.image_url(caption, url)
