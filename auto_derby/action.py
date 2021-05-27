# -*- coding=UTF-8 -*-
# pyright: strict


from . import template
import time
from typing import Iterator, Text, Tuple, Union

import mouse
import win32gui

from . import window

import contextlib


@contextlib.contextmanager
def recover_cursor():
    ox, oy = win32gui.GetCursorPos()
    yield
    mouse.move(ox, oy)


def click_at_window(h_wnd: int, point: Tuple[int, int]):
    point = win32gui.ClientToScreen(h_wnd, point)
    with window.topmost(h_wnd), window.recover_foreground(), recover_cursor():
        mouse.move(point[0], point[1])
        mouse.click()
        time.sleep(0.2)


def click(point: Tuple[int, int]):
    h_wnd = window.get_game()
    click_at_window(h_wnd, point)


def count_image(*tmpl: Union[Text, template.Specification]) -> int:
    ret = 0
    for _ in template.match(template.screenshot(), *tmpl):
        ret += 1
    return ret

def match_image_until_disappear(*tmpl: Union[Text, template.Specification]) -> Iterator[Tuple[template.Specification, Tuple[int, int]]]:
    while True:
        count = 0
        for i in template.match(template.screenshot(), *tmpl):
            count += 1
            yield i
            break # actions will make screenshot outdate
        if count == 0:
            break

def wait_image(*tmpl: Union[Text, template.Specification]) -> Tuple[template.Specification, Tuple[int, int]]:
    while True:
        try:
            return next(template.match(template.screenshot(), *tmpl))
        except StopIteration:
            time.sleep(0.5)

def wait_image_disappear(*tmpl: Union[Text, template.Specification]) -> None:
    while True:
        try:
            next(template.match(template.screenshot(), *tmpl))
            time.sleep(0.5)
        except StopIteration:
            break

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

def move_at_window(h_wnd: int,  point: Tuple[int, int]):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    mouse.move(x, y)


def move(point: Tuple[int, int]):
    move_at_window(window.get_game(), point)


def wheel_at_window(h_wnd: int,delta: int) -> None:
    with window.recover_foreground():
        window.set_forground(h_wnd)
        for _ in range(abs(delta)):
            mouse.wheel(1 if delta > 0 else -1)
            time.sleep(1 / 120.0)
        time.sleep(1)

def wheel(delta: int) -> None:
    wheel_at_window(window.get_game(), delta)


def drag_at_window(h_wnd: int, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1):
    x, y = win32gui.ClientToScreen(h_wnd, point)
    with window.topmost(h_wnd), window.recover_foreground(), recover_cursor():
        mouse.drag(x, y, x+dx, y+dy, duration=duration)


def drag(point: Tuple[int, int], *, dx: int = 0, dy: int = 0, duration: float = 0.1):
    drag_at_window(window.get_game(), point, dx=dx, dy=dy, duration=duration)
