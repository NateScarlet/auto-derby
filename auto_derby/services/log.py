# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import enum

from typing import Dict, Protocol, Text, Union
import PIL.Image
import numpy as np

Image = Union[PIL.Image.Image, np.ndarray]


class Level(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Service(Protocol):
    """
    NOTICE: this interface is unstable,

    change of this interface will not been considered as breaking change until 2022-06-01.
    """

    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        ...

    def image(
        self,
        caption: Text,
        image: Image,
        /,
        *,
        level: Level = Level.INFO,
        layers: Dict[Text, Image] = {},
    ):
        ...
