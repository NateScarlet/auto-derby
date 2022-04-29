# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Protocol, Text, Union
import PIL.Image
import numpy as np

Image = Union[PIL.Image.Image, np.ndarray]


class LogService(Protocol):
    def debug(self, msg: Text, /):
        ...

    def warn(self, msg: Text, /):
        ...

    def info(self, msg: Text, /):
        ...

    def error(self, msg: Text, /):
        ...

    def image(self, caption: Text, image: Image):
        ...

    def image_url(self, caption: Text, url: Text, /):
        ...


class NoOpLogService(LogService):
    def debug(self, msg: Text, /):
        pass

    def warn(self, msg: Text, /):
        pass

    def info(self, msg: Text, /):
        pass

    def error(self, msg: Text, /):
        pass

    def image(self, caption: Text, image: Union[Image, np.ndarray]):
        pass

    def image_url(self, caption: Text, url: Text, /):
        pass
