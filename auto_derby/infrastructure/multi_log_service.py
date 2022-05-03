# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Dict, Sequence, Text

from ..services.log import Image, Level, Service


class MultiLogService(Service):
    @classmethod
    def _iter(cls, *services: Service):
        for i in services:
            if isinstance(i, cls):
                yield from i._s
            else:
                yield i

    def __init__(self, *services: Service) -> None:
        self._s: Sequence[Service] = tuple(self._iter(*services))

    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        for i in self._s:
            i.text(msg, level=level)

    def image(
        self,
        caption: Text,
        image: Image,
        /,
        *,
        level: Level = Level.INFO,
        layers: Dict[Text, Image] = {},
    ):
        for i in self._s:
            i.image(caption, image, level=level, layers=layers)
