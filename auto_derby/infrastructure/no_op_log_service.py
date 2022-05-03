# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Dict, Text

from ..services.log import Image, Level, Service


class NoOpService(Service):
    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        pass

    def image(
        self,
        caption: Text,
        image: Image,
        *,
        level: Level = Level.INFO,
        layers: Dict[Text, Image] = {},
    ):
        pass
