# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Text
import winsound


def play_file(path: Text, wait_finish: bool = False) -> None:
    if not path:
        return
    winsound.PlaySound(
        path,
        winsound.SND_FILENAME | (0 if wait_finish else winsound.SND_ASYNC),
    )
