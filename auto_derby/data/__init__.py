# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from typing import Text
import os

__dirname__ = os.path.dirname(os.path.abspath(__file__))


def path(*paths: Text) -> Text:
    return os.path.join(__dirname__, *paths)
