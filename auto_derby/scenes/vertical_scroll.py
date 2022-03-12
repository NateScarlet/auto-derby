# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Tuple


from .. import action


class VerticalScroll:
    """
    scroll direction is changed after each `complete`.
    `complete` should be called when continuous scroll complete.
    """

    def __init__(
        self,
        *,
        origin: Tuple[int, int],
        page_size: int,
        max_page: int,
    ) -> None:
        # top = 0, bottom = 1
        self._position = 0
        self._same_direction_count = 0
        self._max_same_direction_count = max_page
        self._origin = origin
        self._page_size = page_size
        self._direction_change_count = 0
        self._last_direction = 0

    def on_end(self):
        """this should be called when reached top/bottom."""
        self._position = 1 - self._position
        self._max_same_direction_count = self._same_direction_count + 1
        self._same_direction_count = 0
        self._direction_change_count += 1

    def complete(self):
        """prepare next continuous scroll."""
        self._direction_change_count = 0

    def next(self) -> bool:
        if self._direction_change_count > 6:
            self.complete()
            return False
        if self._same_direction_count == 0:
            # keep first page
            self._same_direction_count += 1
            return True
        direction = 1 if self._position < 0.5 else -1

        action.swipe(
            self._origin,
            dy=-self._page_size * direction,
            duration=0.2,
        )
        # prevent inertial scrolling
        action.tap(self._origin)
        if self._last_direction == direction:
            self._same_direction_count += 1
        else:
            self._same_direction_count = 1
        self._last_direction = direction
        if self._same_direction_count >= self._max_same_direction_count:
            self.on_end()

        return True
