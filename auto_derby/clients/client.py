# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

import PIL.Image


class _g:
    current_client: Client


class Client(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        ...

    def setup(self) -> None:
        pass

    @abstractmethod
    def screenshot(self) -> PIL.Image.Image:
        ...

    @abstractmethod
    def tap(self, point: Tuple[int, int]) -> None:
        ...

    @abstractmethod
    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        ...


# DEPRECATED:


def _legacy_current() -> Client:
    import warnings

    warnings.warn(
        "use `app.device` instead",
        DeprecationWarning,
    )
    return _g.current_client


def _legacy_set_current(c: Client) -> None:
    import warnings

    warnings.warn(
        "use `app.device = ClientDeviceService(c)` instead",
        DeprecationWarning,
    )
    from .. import app
    from ..infrastructure.client_device_service import ClientDeviceService

    app.device = ClientDeviceService(c)
    _g.current_client = c


globals()["current"] = _legacy_current
globals()["set_current"] = _legacy_set_current
