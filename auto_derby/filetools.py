# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import contextlib
import os
from typing import Text


def force_rename(src: Text, dst: Text):
    try:
        os.rename(src, dst)
    except FileExistsError:
        os.unlink(dst)
        os.rename(src, dst)


@contextlib.contextmanager
def atomic_save_path(
    path: Text,
    *,
    temp_suffix: Text = ".tmp",
    backup_suffix: Text = "",
):
    tmp_path = path + temp_suffix
    yield tmp_path
    if backup_suffix:
        backup_path = path + backup_suffix
        try:
            force_rename(path, backup_path)
        except FileNotFoundError:
            pass
    force_rename(tmp_path, path)
