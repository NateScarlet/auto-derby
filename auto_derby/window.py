# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """

import contextlib
import logging
import threading
import time
from typing import Callable, Optional, Set, Text

import win32con
import win32gui

LOGGER = logging.getLogger(__name__)


def message_box(
    msg: Text,
    caption: Text,
    *,
    flags: int = 0,
    h_wnd: int = 0,
    on_close: Optional[Callable[[], None]] = None,
) -> Callable[[], None]:
    def _run():
        win32gui.MessageBox(h_wnd, msg, caption, flags)
        if callable(on_close):
            on_close()
    t = threading.Thread(target=_run)
    t.start()
    h_wnd_set: Set[int] = set()

    def _iter_window(h_wnd: int, _: None):
        if win32gui.GetClassName(h_wnd) != "#32770":  # message box
            return
        h_wnd_set.add(h_wnd)
    assert t.ident is not None
    while not h_wnd_set:
        time.sleep(0.01)
        win32gui.EnumThreadWindows(t.ident, _iter_window, None)
    assert len(h_wnd_set) == 1, h_wnd_set

    def _close():
        for i in h_wnd_set:
            if win32gui.IsWindow(i):
                win32gui.PostMessage(i, win32con.WM_CLOSE, 0, 0)
        t.join()
    return _close


def get_game() -> int:
    return win32gui.FindWindow("UnityWndClass", "umamusume")


def set_client_height(h_wnd: int, height: int):
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    _, _, w, h = win32gui.GetClientRect(h_wnd)
    LOGGER.info("width=%s height=%s", w, h)
    if h == height:
        LOGGER.info("already in wanted height")
        return
    borderWidth = right - left - w
    borderHeight = bottom - top - h
    width = int(height / h * w)
    win32gui.SetWindowPos(
        h_wnd,
        0,
        left,
        top,
        width + borderWidth,
        height + borderHeight,
        0,
    )
    return


@contextlib.contextmanager
def topmost(h_wnd: int):
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    win32gui.SetWindowPos(h_wnd, win32con.HWND_TOPMOST,
                          left, top, right - left, bottom - top, 0)
    yield
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    win32gui.SetWindowPos(h_wnd, win32con.HWND_NOTOPMOST,
                          left, top, right - left, bottom - top, 0)


@contextlib.contextmanager
def recover_foreground():
    fg_h_wnd = win32gui.GetForegroundWindow()
    yield
    try:
        win32gui.SetForegroundWindow(fg_h_wnd)
    except Exception as ex:
        LOGGER.warn("recover foreground window failed: %s", ex)


def info(msg: Text) -> Callable[[], None]:
    return message_box(msg, "auto-derby", h_wnd=get_game())
