# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from typing import Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .race import Race


class g:
    data_path: str = ""
    races: Tuple[Race, ...] = ()
    race_class: Type[Race]
