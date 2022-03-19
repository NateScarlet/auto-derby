# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

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

    print(
        web.prompt(
            f"""\
<h1>test</h1>
<img src="/img.png" />
<a href="/__main__.py">python source file</a>
<form method="POST">
<input name="value" />
<button type="submit" >submit</button>
</form>
""",
            web.Route("/__main__.py", web.File(__file__, "text/plain")),
            web.Route(
                "/img.png",
                web.Blob(
                    img_data.getvalue(),
                    "image/png",
                ),
            ),
            web.Route("/dir/", web.Dir(os.path.dirname(__file__))),
            web.middleware.Debug(),
        )
    )
