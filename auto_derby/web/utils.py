# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


import email.utils
from typing import Text


def format_timestamp(timestamp: float) -> Text:
    return email.utils.formatdate(timestamp, usegmt=True)
