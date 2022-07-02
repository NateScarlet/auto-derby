# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Tuple

from auto_derby import action


from .. import app


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

        rp = action.resize_proxy()

        app.device.swipe(
            (*self._origin, *rp.vector2((0, 5), 540)),
            (self._origin[0], self._origin[1] - self._page_size * direction, 10, 10),
            duration=0.2,
        )
        # prevent inertial scrolling
        app.device.tap((*self._origin, *rp.vector2((5, 5), 540)))
        if self._last_direction == direction:
            self._same_direction_count += 1
        else:
            self._same_direction_count = 1
        self._last_direction = direction
        if self._same_direction_count >= self._max_same_direction_count:
            app.log.text(
                "scrolled in same direction %d times, assuming end is reached"
                % self._same_direction_count,
                level=app.WARN,
            )
            self.on_end()

        return True
