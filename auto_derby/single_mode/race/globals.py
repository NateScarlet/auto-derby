# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .race import Race


class g:
    data_path: str = ""
    result_path: str = ""
    result_max_bytes: int = 10 << 20
    race_class: Type[Race]

    @property
    @classmethod
    def _deprecated_races(cls):
        return tuple(Race.repository.find())


g.races = g._deprecated_races  # type: ignore
