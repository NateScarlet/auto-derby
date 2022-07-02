# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ..services.device import Rect, Service, Image


class NoOpDeviceService(Service):
    def height(self) -> int:
        return 0

    def width(self) -> int:

        return 0

    def screenshot(self, *, max_age: float = 1) -> Image:
        raise NotImplementedError()

    def reset_size(
        self,
    ) -> None:
        pass

    def tap(self, area: Rect) -> None:
        pass

    def swipe(self, start: Rect, end: Rect, *, duration: float = 0.1) -> None:
        pass
