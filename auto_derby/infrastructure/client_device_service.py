# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Tuple

from random import randint

from auto_derby import filetools

from ..services.device import Rect, Service, Image
from ..clients import Client, DMMClient
from .. import template


import datetime as dt


def _random_point(rect: Rect) -> Tuple[int, int]:
    x, y, w, h = rect
    return (randint(x, x + w), randint(y, y + h))


class ClientDeviceService(Service):
    def __init__(self, client: Client) -> None:
        self._c = client
        self._cached_screenshot = (dt.datetime.fromtimestamp(0), Image())

    def height(self) -> int:
        return self._c.height

    def width(self) -> int:
        return self._c.width

    def invalidate_screenshot(self):
        self._cached_screenshot = (dt.datetime.fromtimestamp(0), Image())

    def screenshot(self, *, max_age: float = 1) -> Image:
        from .. import app

        cached_time, _ = self._cached_screenshot
        if cached_time < dt.datetime.now() - dt.timedelta(seconds=max_age):
            new_img = self._c.screenshot().convert("RGB")
            if template.g.last_screenshot_save_path:
                with filetools.atomic_save_path(
                    template.g.last_screenshot_save_path,
                ) as p:
                    new_img.save(p, format="PNG")
            app.log.text("screenshot", level=app.DEBUG)
            self._cached_screenshot = (dt.datetime.now(), new_img)
        return self._cached_screenshot[1]

    def reset_size(
        self,
    ) -> None:
        if isinstance(self._c, DMMClient):
            self._c.setup()

    def tap(self, area: Rect) -> None:
        from .. import app

        app.log.text("tap(%s)" % (area,), level=app.DEBUG)
        self._c.tap(_random_point(area))
        self.invalidate_screenshot()

    def swipe(self, start: Rect, end: Rect, *, duration: float = 0.1) -> None:
        from .. import app

        app.log.text(
            "swipe(%s, %s, duration=%s)" % (start, end, duration), level=app.DEBUG
        )
        p1 = _random_point(start)
        p2 = _random_point(end)
        self._c.swipe(p1, dx=p2[0] - p1[0], dy=p2[1] - p1[1], duration=duration)
        self.invalidate_screenshot()
