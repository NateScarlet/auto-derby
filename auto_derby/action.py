# -*- coding=UTF-8 -*-
# pyright: strict

from . import mathtools
from . import template
import time
from typing import Callable, Iterable, Iterator, Text, Tuple, TypeVar, Union

from . import clients


def resize_proxy() -> mathtools.ResizeProxy:
    """Resize proxy to current client width."""
    return mathtools.ResizeProxy(clients.current().width)


def tap(point: Tuple[int, int]):
    clients.current().tap(point)
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
    *tmpl: Union[Text, template.Specification],
    timeout: float = float("inf"),
) -> Tuple[template.Specification, Tuple[int, int]]:
    deadline = time.time() + timeout
    while True:
        try:
            return next(template.match(template.screenshot(max_age=0), *tmpl))
        except StopIteration:
            if time.time() > deadline:
                raise TimeoutError()
            time.sleep(0.01)


def wait_image_pos(
    *tmpl: Union[Text, template.Specification],
    pos: Tuple[int, int],
    timeout: float = float("inf"),
) -> template.Specification:
    deadline = time.time() + timeout
    x, y = pos
    max_width, max_height = (0, 0)
    for i in tmpl:
        width, height = template.load(i.name if isinstance(i, template.Specification) else i).size
        max_width = max(max_width, width)
        max_height = max(max_height, height)

    bbox = (
        x,
        y,
        x + max_width,
        y + max_height,
    )
    while True:
        try:
            t, _ = next(
                template.match(template.screenshot(max_age=0).crop(bbox), *tmpl)
            )
            return t
        except StopIteration:
            if time.time() > deadline:
                raise TimeoutError()
            time.sleep(0.01)


def wait_image_stable(
    *tmpl: Union[Text, template.Specification],
    duration: float = 1.0,
    timeout: float = float("inf"),
) -> Tuple[template.Specification, Tuple[int, int]]:
    deadline = time.time() + timeout
    t, last_pos = wait_image(*tmpl, timeout=timeout)
    last_changed_time = time.time()
    while True:
        time.sleep(0.01)
        _, pos = wait_image(t, timeout=deadline - time.time())
        if pos != last_pos:
            last_changed_time = time.time()
        if time.time() - last_changed_time > duration:
            break
        if time.time() > deadline:
            raise TimeoutError()
        last_pos = pos
    return t, last_pos


T = TypeVar("T")


def run_with_retry(fn: Callable[[], T], max_retry: int = 10, delay: float = 1) -> T:
    try:
        return fn()
    except Exception:
        if max_retry <= 0:
            raise
        time.sleep(delay)
        return run_with_retry(fn, max_retry - 1, delay)


def wait_image_disappear(*tmpl: Union[Text, template.Specification]) -> None:
    while True:
        try:
            next(template.match(template.screenshot(max_age=0), *tmpl))
            time.sleep(0.5)
        except StopIteration:
            break


def tap_image(
    name: Union[Text, template.Specification], *, x: int = 0, y: int = 0
) -> bool:
    try:
        name, pos = next(template.match(template.screenshot(), name))
        tap((pos[0] + x, pos[1] + y))
        return True
    except StopIteration:
        return False


def wait_tap_image(
    name: Union[Text, template.Specification], *, x: int = 0, y: int = 0
) -> None:
    _, last_pos = wait_image(name)
    while True:
        _, pos = wait_image(name)
        if pos == last_pos:
            break
        last_pos = pos
    tap((pos[0] + x, pos[1] + y))


def swipe(point: Tuple[int, int], *, dx: int = 0, dy: int = 0, duration: float = 0.1):
    clients.current().swipe(point, dx=dx, dy=dy, duration=duration)
    template.invalidate_screeshot()


def reset_client_size() -> None:
    client = clients.current()
    if isinstance(client, clients.DMMClient):
        client.setup()
