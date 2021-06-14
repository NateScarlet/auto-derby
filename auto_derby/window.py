# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """

import contextlib
import logging
import threading
import time
from ctypes import windll
from typing import Callable, Dict, Iterator, Literal, Optional, Set, Text, Tuple

import PIL.Image
import PIL.ImageGrab
import win32con
import win32gui

LOGGER = logging.getLogger(__name__)
_IS_ADMIN = bool(windll.shell32.IsUserAnAdmin())


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


_INIT_ONCE: Dict[Literal["value"], bool] = {"value": False}


def init():
    if _INIT_ONCE["value"]:
        return
    _INIT_ONCE["value"] = True
    # Window size related function will returns incorrect result
    # if we don't make python process dpi aware
    # https://github.com/NateScarlet/auto-derby/issues/11
    windll.user32.SetProcessDPIAware()


def set_client_size(h_wnd: int, width: int, height: int):
    init()
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    _, _, w, h = win32gui.GetClientRect(h_wnd)
    LOGGER.info("width=%s height=%s", w, h)
    if h == height and w == width:
        LOGGER.info("already in wanted size")
        return
    borderWidth = right - left - w
    borderHeight = bottom - top - h
    win32gui.SetWindowPos(
        h_wnd, 0, left, top, width + borderWidth, height + borderHeight, 0
    )
    set_client_size(h_wnd, width, height)  # repeat until exact match
    return


@contextlib.contextmanager
def topmost(h_wnd: int):
    init()
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    win32gui.SetWindowPos(
        h_wnd, win32con.HWND_TOPMOST, left, top, right - left, bottom - top, 0
    )
    yield
    left, top, right, bottom = win32gui.GetWindowRect(h_wnd)
    win32gui.SetWindowPos(
        h_wnd, win32con.HWND_NOTOPMOST, left, top, right - left, bottom - top, 0
    )


def set_forground(h_wnd: int) -> None:
    win32gui.SetForegroundWindow(h_wnd)


@contextlib.contextmanager
def recover_foreground():
    fg_h_wnd = win32gui.GetForegroundWindow()
    yield
    time.sleep(0.1)  # switch too fast may cause issue
    try:
        win32gui.SetForegroundWindow(fg_h_wnd)
    except Exception as ex:
        LOGGER.warn("recover foreground window failed: %s", ex)


def info(msg: Text) -> Callable[[], None]:
    return message_box(msg, "auto-derby", h_wnd=get_game() if _IS_ADMIN else 0)


import mouse


@contextlib.contextmanager
def recover_cursor():
    ox, oy = win32gui.GetCursorPos()
    yield
    mouse.move(ox, oy)


def click_at(h_wnd: int, point: Tuple[int, int]):
    point = win32gui.ClientToScreen(h_wnd, point)
    with topmost(h_wnd), recover_foreground(), recover_cursor():
        mouse.move(point[0], point[1])
        mouse.click()
        time.sleep(0.2)


def drag_at(
    h_wnd: int, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    with topmost(h_wnd), recover_foreground(), recover_cursor():
        mouse.drag(x, y, x + dx, y + dy, duration=duration)


@contextlib.contextmanager
def _pressing_mouse(button: Text = "left"):
    if mouse.is_pressed(button):
        mouse.release()
    mouse.press(button)
    yield
    mouse.release(button)


def drag_through_at(
    h_wnd: int, *points: Tuple[int, int], duration: float = 0.05
) -> Iterator[Tuple[int, int]]:
    with recover_cursor(), recover_foreground():
        set_forground(h_wnd)
        move_at(h_wnd, points[0])
        yield points[0]
        with _pressing_mouse(), topmost(h_wnd):
            for p in points[1:]:
                x, y = win32gui.ClientToScreen(h_wnd, p)
                mouse.move(x, y, duration=duration)
                yield p


def wheel_at(h_wnd: int, delta: int) -> None:
    with recover_foreground():
        set_forground(h_wnd)
        for _ in range(abs(delta)):
            mouse.wheel(1 if delta > 0 else -1)
            time.sleep(1 / 120.0)
        time.sleep(1)


def move_at(h_wnd: int, point: Tuple[int, int]):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    mouse.move(x, y)


def screenshot(h_wnd: int) -> PIL.Image.Image:
    init()
    # XXX: BitBlt capture not work, background window is not supportted
    # Maybe use WindowsGraphicsCapture like obs do
    with topmost(h_wnd):
        # not use GetWindowRect to exclude border
        _, _, w, h = win32gui.GetClientRect(h_wnd)
        x, y = win32gui.ClientToScreen(h_wnd, (0, 0))
        left, top, right, bottom = x, y, x + w, y + h
        bbox = (left, top, right, bottom)
        return PIL.ImageGrab.grab(bbox, True, True)


# TODO: move client inside visible area
