# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable

from .. import Context


class g:
    ignore_training_commands: Callable[[Context], bool] = lambda _: False
