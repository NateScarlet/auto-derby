# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from contextlib import closing
from datetime import datetime
import time

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../.."))

import logging

import web
from PIL import Image
import io

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    img_data = io.BytesIO()
    Image.new("RGB", (200, 200), (255, 0, 0)).save(img_data, "PNG"),

    with closing(
        web.stream(
            f"""\
    <h1>test</h1>
    <img src="/img.png" />
    <a href="/__main__.py">python source file</a>
    <form method="POST">
    <input name="value" />
    <button type="submit" >submit</button>
</form>
""",
            web.Route(
                "/img.png",
                web.Blob(
                    img_data.getvalue(),
                    "image/png",
                ),
            ),
            web.Route("/dir/", web.Dir(os.path.dirname(__file__))),
            web.middleware.Debug(),
            buffer_path="stream.log",
            mimetype="text/plain",
        )
    ) as s:
        while True:
            s.write((datetime.now().isoformat() + "\n").encode("utf-8"))
            time.sleep(0.5)
