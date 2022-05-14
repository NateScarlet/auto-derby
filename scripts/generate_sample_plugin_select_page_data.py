# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Text


if True:
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import json
from auto_derby import plugin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="auto_derby/web/src/samples/plugin_select.json",
    )
    args = parser.parse_args()
    path: Text = args.path
    plugin.reload()
    plugins = [
        {"name": name, "doc": (p.__doc__ or "").strip()}
        for name, p in plugin.g.plugins.items()
        if ".local" not in name and not plugin.is_deprecated(name)
    ]
    data = {
        "type": "PLUGIN_SELECT",
        "plugins": plugins,
    }
    if path == "-":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
