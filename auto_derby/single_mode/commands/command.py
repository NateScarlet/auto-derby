# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Text
from abc import ABC, abstractmethod
from ..context import Context


class Command(ABC):
    @abstractmethod
    def execute(self, ctx: Context) -> None:
        ...

    def name(self) -> Text:
        ret = self.__class__.__name__
        if ret.endswith("Command"):
            ret = ret[:-7]
        return ret

    def score(self, ctx: Context) -> float:
        return 0
