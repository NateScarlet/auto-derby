# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import logging
from typing import Text

from auto_derby import imagetools

from ..log import Image, Level, Service


class LoggingLogService(Service):
    def __init__(self, logger: logging.Logger) -> None:
        self._l = logger

    def _level_of(self, l: Level) -> int:
        if l == Level.DEBUG:
            return logging.DEBUG
        if l == Level.INFO:
            return logging.INFO
        if l == Level.WARN:
            return logging.WARNING
        return logging.ERROR

    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        self._l.log(
            self._level_of(level),
            msg,
        )

    def image(self, caption: Text, image: Image, *, level: Level = Level.INFO):
        img = imagetools.pil_image_of(image)
        if img.width * img.height < 20000:
            return self._l.log(
                self._level_of(level),
                "%s: %s",
                caption,
                imagetools.data_url(img),
            )

        self._l.log(
            self._level_of(level),
            "%s: w=%d h=%d",
            caption,
            img.width,
            img.height,
        )
