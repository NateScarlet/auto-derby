# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import logging

from typing import Protocol, Text

_LOGGER = logging.getLogger(__name__)


class Webview(Protocol):
    def open(self, url: Text) -> None:
        ...

    def shutdown(self) -> None:
        ...


class NoOpWebview(Webview):
    def open(self, url: Text) -> None:
        pass

    def shutdown(self) -> None:
        pass
