# -*- coding=UTF-8 -*-
# pyright: strict


from . import template
import time
from typing import Text, Tuple, Union

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
    with window.topmost(h_wnd), window.recover_foreground(), cursor_at(point):
        mouse.click()
        time.sleep(0.2)


def click(point: Tuple[int, int]):
    h_wnd = window.get_game()
    click_at_window(h_wnd, point)


def count_image(*name: Text) -> int:
    ret = 0
    for _ in template.match(template.screenshot(), *name):
        ret += 1
    return ret


def wait_image(*tmpl: Union[Text, template.Specification]) -> Tuple[template.Specification, Tuple[int, int]]:
    while True:
        try:
            return next(template.match(template.screenshot(), *tmpl))
        except StopIteration:
            time.sleep(0.5)


def click_image(name: Union[Text, template.Specification], *, x: int = 0, y: int = 0) -> bool:
    try:
        name, pos = next(template.match(template.screenshot(), name))
        click((pos[0] + x, pos[1] + y))
        return True
    except StopIteration:
        return False


def wait_click_image(name: Text, *, x: int = 0, y: int = 0) -> None:
    _, pos = wait_image(name)
    click((pos[0]+x, pos[1]+y))


def move(h_wnd: int, x: int, y: int):
    x, y = win32gui.ClientToScreen(h_wnd, (x, y))
    mouse.move(x, y)


def drag_at_window(h_wnd: int, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    with window.topmost(h_wnd), window.recover_foreground():
        mouse.drag(x, y, x+dx, y+dy, duration=duration)


def drag(point: Tuple[int, int], *, dx: int = 0, dy: int = 0, duration: float = 0.1):
    drag_at_window(window.get_game(), point, dx=dx, dy=dy, duration=duration)
