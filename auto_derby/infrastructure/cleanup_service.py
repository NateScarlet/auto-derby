# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import List

from ..services.cleanup import Callback, Service


class CleanupService(Service):
    def __init__(self) -> None:
        self._callbacks: List[Callback] = []

    def add(self, cb: Callback) -> None:
        self._callbacks.append(cb)

    def run(self) -> None:
        while self._callbacks:
            self._callbacks.pop()()

    def __enter__(self) -> Service:
        return self

    def __exit__(self, *_) -> None:
        self.run()
