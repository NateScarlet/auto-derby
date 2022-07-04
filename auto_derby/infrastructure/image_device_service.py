# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from ..services.device import Rect, Service, Image


class ImageDeviceService(Service):
    def __init__(self, image: Image) -> None:
        self._img = image

    def height(self) -> int:
        return self._img.height

    def width(self) -> int:
        return self._img.width

    def screenshot(self, *, max_age: float = 1) -> Image:
        return self._img

    def reset_size(
        self,
    ) -> None:
        pass

    def tap(self, area: Rect) -> None:
        raise NotImplementedError()

    def swipe(self, start: Rect, end: Rect, *, duration: float = 0.1) -> None:
        raise NotImplementedError()
