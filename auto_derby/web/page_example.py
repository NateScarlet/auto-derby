# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import uuid

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../../.."))

import logging

from auto_derby import web, single_mode
from PIL import Image
import io

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    img_data = io.BytesIO()
    Image.new("RGB", (200, 200), (255, 0, 0)).save(img_data, "PNG"),

    token = uuid.uuid4().hex
    print(
        web.prompt(
            web.page.render(
                {
                    "type": "SINGLE_MODE_ITEM_SELECT",
                    "imageURL": "/img.png",
                    "submitURL": "?token=" + token,
                    "defaultValue": 1,
                    "options": [
                        i.to_dict() for i in single_mode.item.game_data.iterate()
                    ],
                }
            ),
            web.page.ASSETS,
            web.Route(
                "/img.png",
                web.Blob(
                    img_data.getvalue(),
                    "image/png",
                ),
            ),
            web.middleware.Debug(),
            web.middleware.TokenAuth(token, ("POST",)),
        )
    )
