# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Any, Dict, Text

# from ._prompt import prompt

import os
import json
from .middleware import Dir, Route

__dirname__ = os.path.dirname(os.path.abspath(__file__))

# TODO: add image debug page


def render(
    data: Dict[Text, Any],
) -> Text:
    """see ./src/page-data.ts for accepted data format."""
    with open(os.path.join(__dirname__, "dist/index.html"), encoding="utf-8") as f:
        template = f.read()
    return template.replace("<!-- inject data here -->", json.dumps(data))


ASSETS = Route("/assets/", Dir(os.path.join(__dirname__, "dist/assets")))
