# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
from ctypes import windll
from typing import Optional, Tuple

import PIL.Image
import PIL.ImageGrab
import win32con
import win32gui

from .client import Client
from .. import window


LOGGER = logging.getLogger(__name__)

_IS_ADMIN = bool(windll.shell32.IsUserAnAdmin())


class DMMClient(Client):
    def __init__(self, h_wnd: int):
        self.h_wnd = h_wnd
        self._height, self._width = 0, 0

    @classmethod
    def find(cls) -> Optional[DMMClient]:
        h_wnd = win32gui.FindWindow("UnityWndClass", "umamusume")
        if not h_wnd:
            return None
        return cls(h_wnd)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def set_size(self, width: int, height: int):
        window.init()
        win32gui.ShowWindow(self.h_wnd, win32con.SW_NORMAL)
        window.set_client_size(self.h_wnd, width, height)
        self._width, self._height = width, height
        return

    def setup(self) -> None:
        if not _IS_ADMIN:
            raise PermissionError("DMMClient: require admin permission")
        self.set_size(540, 960)
        window.set_foreground(self.h_wnd)
        LOGGER.info("foregrounded game window: handle=%s", self.h_wnd)

    def screenshot(self) -> PIL.Image.Image:
        return window.screenshot(self.h_wnd)

    def tap(self, point: Tuple[int, int]) -> None:
        LOGGER.debug("tap: point=%s", point)
        window.click_at(self.h_wnd, point)

    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        LOGGER.debug("swipe: point=%s dx=%d dy=%d", point, dx, dy)
        window.drag_at(self.h_wnd, point, dx=dx, dy=dy, duration=duration)
