# -*- coding=UTF-8 -*-
# pyright: strict


from . import template
import time
from typing import Text, Tuple

import mouse
import win32gui

from . import window

import contextlib


@contextlib.contextmanager
def cursor_at(point: Tuple[int, int]):
    ox, oy = win32gui.GetCursorPos()
    x, y = point
    mouse.move(x, y)
    yield
    mouse.move(ox, oy)


def click_at_window(h_wnd: int, point: Tuple[int, int]):
    point = win32gui.ClientToScreen(h_wnd, point)
    with window.topmost(h_wnd), cursor_at(point):
        mouse.click()
        time.sleep(0.2)


def click(point: Tuple[int, int]):
    h_wnd = window.get_game()
    click_at_window(h_wnd, point)


def count_image(*name: Text) -> bool:
    h_wnd = window.get_game()
    match = template.match(template.screenshot(h_wnd), *name)
    if not match:
        return False
    return True


def wait_image(*name: Text) -> Tuple[Text, Tuple[int, int]]:
    h_wnd = window.get_game()
    while True:
        match = template.match(template.screenshot(h_wnd), *name)
        if match:
            return match
        time.sleep(0.5)


def click_image(name: Text, *, x: int = 0, y: int = 0) -> bool:
    h_wnd = window.get_game()
    match = template.match(template.screenshot(h_wnd), name)
    if not match:
        return False
    click_at_window(h_wnd, (match[1][0] + x, match[1][1] + y))
    return True


def wait_click_image(name: Text, *, x: int = 0, y: int = 0) -> None:
    wait_image(name)
    click_image(name, x=x, y=y)


def move(h_wnd: int, x: int, y: int):
    x, y = win32gui.ClientToScreen(h_wnd, (x, y))
    mouse.move(x, y)
