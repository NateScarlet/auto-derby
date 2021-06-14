# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

from typing import Iterator, Tuple

import PIL.Image
import PIL.ImageGrab

from .client import Client


class SingleImageClient(Client):
    """Use single image as client for test."""

    def __init__(self, img: PIL.Image.Image):
        self.image = img

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    def screenshot(self) -> PIL.Image.Image:
        return self.image

    def click(self, point: Tuple[int, int]) -> None:
        raise NotImplementedError()

    def drag(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        raise NotImplementedError()

    def drag_through(
        self, *points: Tuple[int, int], duration: float = 0.02
    ) -> Iterator[Tuple[int, int]]:
        raise NotImplementedError()

    def wheel(self, point: Tuple[int, int], delta: int) -> None:
        raise NotImplementedError()
