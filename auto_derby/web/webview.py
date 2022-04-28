# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import logging
import time
import webbrowser
from typing import Protocol, Text

_LOGGER = logging.getLogger(__name__)

class Webview(Protocol):
    def open(self, url: Text) -> None:
        ...

    def shutdown(self) -> None:
        ...


class NoOpWebview(Webview):
    def open(self, url: Text) -> None:
        pass

    def shutdown(self) -> None:
        pass

class DefaultWebview(Webview):
    def __init__(self) -> None:
        self.url = ""

    def open(self, url: Text):
        self.url = url
        try:
            import win32gui

            self.h_wnd = win32gui.GetForegroundWindow()
        except ImportError:
            self.h_wnd = 0
        webbrowser.open(url)

    def shutdown(self) -> None:
        if not self.url.startswith("http://127.0.0.1:"):
            return

        # press Ctrl+W
        try:
            import win32api
            import win32con
        except ImportError:
            _LOGGER.info(
                "`win32api`/`win32con` module not found, browser tab need to be closed manually"
            )
            return
        VK_W = int.from_bytes(b"W", "big")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(VK_W, 0, 0, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_W, 0, win32con.KEYEVENTF_KEYUP, 0)

        time.sleep(0.1)  # wait chrome response

        try:
            import win32gui

            if self.h_wnd:
                win32gui.SetForegroundWindow(self.h_wnd)
        except Exception:
            pass

