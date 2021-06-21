# -*- coding=UTF-8 -*-
# pyright: strict

from . import mathtools
from . import template
import time
from typing import Callable, Iterable, Iterator, Text, Tuple, Union

from . import clients


def resize_proxy() -> mathtools.ResizeProxy:
    """Resize proxy to current client width."""
    return mathtools.ResizeProxy(clients.current().width)


def click(point: Tuple[int, int]):
    clients.current().click(point)
    template.invalidate_screeshot()


def count_image(*tmpl: Union[Text, template.Specification]) -> int:
    ret = 0
    for _ in template.match(template.screenshot(), *tmpl):
        ret += 1
    return ret


def match_image_until_disappear(
    *tmpl: Union[Text, template.Specification],
    sort: Callable[
        [Iterator[Tuple[template.Specification, Tuple[int, int]]]],
        Iterable[Tuple[template.Specification, Tuple[int, int]]],
    ] = lambda x: x,
) -> Iterator[Tuple[template.Specification, Tuple[int, int]]]:
    while True:
        count = 0
        for i in sort(template.match(template.screenshot(max_age=0), *tmpl)):
            count += 1
            yield i
            break  # actions will make screenshot outdate
        if count == 0:
            break


def wait_image(
    *tmpl: Union[Text, template.Specification]
) -> Tuple[template.Specification, Tuple[int, int]]:
    while True:
        try:
            return next(template.match(template.screenshot(max_age=0), *tmpl))
        except StopIteration:
            time.sleep(0.01)


def wait_image_disappear(*tmpl: Union[Text, template.Specification]) -> None:
    while True:
        try:
            next(template.match(template.screenshot(max_age=0), *tmpl))
            time.sleep(0.5)
        except StopIteration:
            break


def click_image(
    name: Union[Text, template.Specification], *, x: int = 0, y: int = 0
) -> bool:
    try:
        name, pos = next(template.match(template.screenshot(), name))
        click((pos[0] + x, pos[1] + y))
        return True
    except StopIteration:
        return False


def wait_click_image(
    name: Union[Text, template.Specification], *, x: int = 0, y: int = 0
) -> None:
    _, pos = wait_image(name)
    click((pos[0] + x, pos[1] + y))


def wheel(point: Tuple[int, int], delta: int) -> None:
    clients.current().wheel(point, delta)
    template.invalidate_screeshot()


def drag(point: Tuple[int, int], *, dx: int = 0, dy: int = 0, duration: float = 0.03):
    clients.current().drag(point, dx=dx, dy=dy, duration=duration)
    template.invalidate_screeshot()
