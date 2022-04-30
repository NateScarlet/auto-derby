# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import traceback
from typing import Any, Text, Tuple

from auto_derby import imagetools

from ..log import Image, Level, Service


class LoggingLogService(Service):
    _infra_module_prefix = ".".join(__name__.split(".")[:-1]) + "."

    def _find_logger(self) -> Tuple[logging.Logger, int]:
        stack_level = 0
        for f, _ in traceback.walk_stack(None):
            stack_level += 1
            name = f.f_globals.get("__name__", "unknown")
            if not name.startswith(self._infra_module_prefix):
                return logging.getLogger(name), stack_level
        return logging.root, stack_level

    def _level_of(self, l: Level) -> int:
        if l == Level.DEBUG:
            return logging.DEBUG
        if l == Level.INFO:
            return logging.INFO
        if l == Level.WARN:
            return logging.WARNING
        return logging.ERROR

    def _log(self, level: Level, msg: Text, *args: Any):
        l, stack_level = self._find_logger()
        l.log(
            self._level_of(level),
            msg,
            *args,
            stacklevel=stack_level,
        )

    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        self._log(
            level,
            msg,
        )

    def image(self, caption: Text, image: Image, *, level: Level = Level.INFO):
        img = imagetools.pil_image_of(image)
        if img.width * img.height < 20000:
            return self._log(
                level,
                "%s: %s",
                caption,
                imagetools.data_url(img),
            )

        self._log(
            level,
            "image %sx%s: %s",
            img.width,
            img.height,
            caption,
        )
