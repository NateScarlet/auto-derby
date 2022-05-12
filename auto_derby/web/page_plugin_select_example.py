# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import uuid

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../../.."))

import logging

from auto_derby import web, plugin

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    token = uuid.uuid4().hex
    print(
        web.prompt(
            web.page.render(
                {
                    "type": "PLUGIN_SELECT",
                    "submitURL": "?token=" + token,
                    "plugins": [
                        {"name": name, "doc": (p.__doc__ or "").strip()}
                        for name, p in plugin.g.plugins.items()
                        if not plugin.is_deprecated(name)
                    ],
                }
            ),
            web.page.ASSETS,
            web.middleware.Debug(),
            web.middleware.TokenAuth(token, ("POST",)),
        )
    )
