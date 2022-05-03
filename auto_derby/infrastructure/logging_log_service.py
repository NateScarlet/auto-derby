# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, Text, Tuple

from .. import imagetools
from ..services.log import Image, Level, Service


class LoggingLogService(Service):
    _infra_module_prefix = ".".join(__name__.split(".")[:-1]) + "."
    max_inline_image_pixels = 5000

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

    def image(
        self,
        caption: Text,
        image: Image,
        *,
        level: Level = Level.INFO,
        layers: Dict[Text, Image] = {},
    ):
        img = imagetools.pil_image_of(image)
        fields = {"caption": caption, "width": img.width, "height": img.height}
        if layers:
            fields["layers"] = ",".join(layers.keys())
        if img.width * img.height < self.max_inline_image_pixels:
            fields["url"] = imagetools.data_url(img)
        fields_text = " ".join(f"{k}={v}" for k, v in fields.items())
        return self._log(
            level,
            "image: %s",
            fields_text,
        )
