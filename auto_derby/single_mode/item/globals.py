# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Text


from ... import data


# TODO: add config
class g:
    data_path: Text = data.path("single_mode_items.jsonl")
    label_path: Text = ""
