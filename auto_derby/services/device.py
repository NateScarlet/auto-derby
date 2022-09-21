# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Callable, Protocol, Tuple

from PIL.Image import Image

Callback = Callable[[], None]

Rect = Tuple[int, int, int, int]  # (x, y, w, h)


class Service(Protocol):
    def height(self) -> int:
        ...

    def width(self) -> int:
        ...

    def screenshot(self, *, max_age: float = 1) -> Image:
        ...

    def reset_size(
        self,
    ) -> None:
        ...

    def tap(self, area: Rect) -> None:
        ...

    def swipe(self, start: Rect, end: Rect, /, *, duration: float = 0.1) -> None:
        ...
