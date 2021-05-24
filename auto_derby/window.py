# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """

import win32con
import contextlib

import win32gui
import logging
LOGGER = logging.getLogger(__name__)


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
