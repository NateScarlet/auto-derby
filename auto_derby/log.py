# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Dict, Protocol, Text, Union
from PIL.Image import Image
import numpy as np


class LogService(Protocol):
    def debug(self, msg: Text, data: Dict[Text, Text] = ..., /):
        ...

    def warn(self, msg: Text, data: Dict[Text, Text] = ..., /):
        ...

    def info(self, msg: Text, data: Dict[Text, Text] = ..., /):
        ...

    def error(self, msg: Text, data: Dict[Text, Text] = ..., /):
        ...

    def image(self, image: Union[Image, np.ndarray]):
        ...

    def image_url(self, url: Text, /):
        ...
