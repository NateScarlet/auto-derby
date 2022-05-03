# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable, Protocol

Callback = Callable[[], None]


class Service(Protocol):
    def add(self, cb: Callback) -> None:
        ...

    def run(self) -> None:
        ...

    def __enter__(self) -> Service:
        ...

    def __exit__(self, *_) -> None:
        ...
