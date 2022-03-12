# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Tuple


from .. import action


class MenuScroll:
    def __init__(self, origin: Tuple[int, int], page_size: int) -> None:
        # top = 0, bottom = 1
        self._position = 0
        self._same_direction_count = 0
        self._max_same_direction_count = 5
        self._origin = origin
        self._page_size = page_size

    def next_page(self, direction: int = 0) -> None:
        if direction == 0:
            direction = 1 if self._position < 0.5 else -1

        action.swipe(
            self._origin,
            dy=-self._page_size * direction,
            duration=0.2,
        )
        # prevent inertial scrolling
        action.tap(self._origin)
        self._same_direction_count += 1
        if self._same_direction_count >= self._max_same_direction_count:
            self.change_direction()

    def change_direction(self):
        self._position = 1 - self._position
        self._max_same_direction_count = self._same_direction_count + 1
        self._same_direction_count = 0
