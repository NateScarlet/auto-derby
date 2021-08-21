# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Type, Dict

if TYPE_CHECKING:
    from .training import Training
    from .partner import Partner


class g:
    training_class: Type[Training]
    partner_class: Type[Partner]
    target_levels: Dict[int, int] = {}
    image_path: str = ""
