# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict, Literal, Tuple
import PIL.Image


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

    # TODO: rename to tap
    @abstractmethod
    def tap(self, point: Tuple[int, int]) -> None:
        ...

    @abstractmethod
    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        ...


_CURRENT_CLIENT: Dict[Literal["value"], Client] = {}


def current() -> Client:
    return _CURRENT_CLIENT["value"]


def set_current(c: Client) -> None:
    _CURRENT_CLIENT["value"] = c
