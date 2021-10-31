# -*- coding=UTF-8 -*-
# pyright: strict
"""umamusume pertty derby automation.  """

import contextlib
import logging
import sys
import threading
import time
from ctypes import windll
from typing import Callable, Optional, Set, Text, Tuple

import mouse
import PIL.Image
import PIL.ImageGrab
import win32con
import win32gui
import win32ui

LOGGER = logging.getLogger(__name__)


class _g:
    init_once = False


class g:
    use_legacy_screenshot = False
    on_foreground_will_change = lambda: None


def message_box(
    msg: Text,
    caption: Text,
    *,
    flags: int = 0,
    h_wnd: int = 0,
    on_close: Optional[Callable[[int], None]] = None,
) -> Callable[[], None]:
    def _run():
        res = win32gui.MessageBox(h_wnd, msg, caption, flags)
        if callable(on_close):
            on_close(res)

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


def init():
    if _g.init_once:
        return
    _g.init_once = True
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


def set_foreground(h_wnd: int) -> None:
    g.on_foreground_will_change()
    LOGGER.debug("set foreground window: h_wnd=%s", h_wnd)
    try:
        win32gui.SetForegroundWindow(h_wnd)
    except Exception as ex:
        LOGGER.warn(
            "set foreground window failed: h_wnd=%s error='%s'",
            h_wnd,
            ex,
        )


def set_forground(h_wnd: int) -> None:
    import warnings

    warnings.warn("use set_foreground instead", DeprecationWarning)
    return set_foreground(h_wnd)


@contextlib.contextmanager
def recover_foreground():
    h_wnd = win32gui.GetForegroundWindow()
    LOGGER.debug("foreground window: h_wnd=%s", h_wnd)
    g.on_foreground_will_change()
    yield
    time.sleep(0.1)  # switch too fast may cause issue
    set_foreground(h_wnd)


def info(msg: Text) -> Callable[[], None]:
    return message_box(msg, "auto-derby")


@contextlib.contextmanager
def recover_cursor():
    ox, oy = win32gui.GetCursorPos()
    yield
    mouse.move(ox, oy)


def click_at(h_wnd: int, point: Tuple[int, int]):
    point = win32gui.ClientToScreen(h_wnd, point)
    with recover_foreground(), recover_cursor(), topmost(h_wnd):
        mouse.move(point[0], point[1])
        mouse.click()
        time.sleep(0.2)


def drag_at(
    h_wnd: int, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    with recover_foreground(), recover_cursor(), topmost(h_wnd):
        mouse.drag(x, y, x + dx, y + dy, duration=duration)
        move_at(h_wnd, (-1, -1))
        time.sleep(0.05)


def wheel_at(h_wnd: int, delta: int) -> None:
    with recover_foreground():
        set_foreground(h_wnd)
        for _ in range(abs(delta)):
            mouse.wheel(1 if delta > 0 else -1)
            time.sleep(1 / 120.0)
        time.sleep(1)


def move_at(h_wnd: int, point: Tuple[int, int]):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    mouse.move(x, y)


def screenshot_pil_crop(h_wnd: int) -> PIL.Image.Image:
    init()
    # XXX: BitBlt capture not work, background window is not supportted
    # Maybe use WindowsGraphicsCapture like obs do
    with topmost(h_wnd):
        # not use GetWindowRect to exclude border
        win32gui.ShowWindow(h_wnd, win32con.SW_NORMAL)
        _, _, w, h = win32gui.GetClientRect(h_wnd)
        x, y = win32gui.ClientToScreen(h_wnd, (0, 0))
        left, top, right, bottom = x, y, x + w, y + h
        bbox = (left, top, right, bottom)
        return PIL.ImageGrab.grab(bbox, True, True)


# https://docs.microsoft.com/en-us/windows/win32/winprog/using-the-windows-headers
_WIN32_WINNT_WINBLUE = 0x0603


def _win_ver():
    v = sys.getwindowsversion()
    return v.major << 8 | v.minor


_WIN32_WINNT = _win_ver()

PW_CLIENT_ONLY = 1 << 0
# https://stackoverflow.com/a/40042587
PW_RENDERFULLCONTENT = 1 << 1 if _WIN32_WINNT >= _WIN32_WINNT_WINBLUE else 0
if PW_RENDERFULLCONTENT == 0:
    LOGGER.info(
        (
            "background screenshot not work before windows8.1, "
            "will use legacy screenshot."
        )
    )
    g.use_legacy_screenshot = True


# https://stackoverflow.com/a/24352388
def screenshot_print_window(h_wnd: int) -> PIL.Image.Image:
    window_dc = win32gui.GetWindowDC(h_wnd)
    handle_dc = win32ui.CreateDCFromHandle(window_dc)
    win32gui.ShowWindow(h_wnd, win32con.SW_NORMAL)
    _, _, width, height = win32gui.GetClientRect(h_wnd)
    compatible_dc = handle_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    try:
        bitmap.CreateCompatibleBitmap(handle_dc, width, height)

        compatible_dc.SelectObject(bitmap)
        result = windll.user32.PrintWindow(
            h_wnd,
            compatible_dc.GetSafeHdc(),
            PW_CLIENT_ONLY | PW_RENDERFULLCONTENT,
        )
        if result != 1:
            raise RuntimeError("print window failed: %s" % result)
        return PIL.Image.frombuffer(
            "RGB", (width, height), bitmap.GetBitmapBits(True), "raw", "BGRX", 0, 1
        )
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        handle_dc.DeleteDC()
        compatible_dc.DeleteDC()
        win32gui.ReleaseDC(h_wnd, window_dc)


def screenshot(h_wnd: int) -> PIL.Image.Image:
    if g.use_legacy_screenshot:
        return screenshot_pil_crop(h_wnd)
    return screenshot_print_window(h_wnd)
