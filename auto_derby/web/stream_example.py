# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import io
import logging
import threading
import time
import webbrowser
from datetime import datetime

from PIL import Image

import web

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    img_data = io.BytesIO()
    Image.new("RGB", (200, 200), (255, 0, 0)).save(img_data, "PNG"),

    with web.Stream("stream.log", "text/plain") as stream, web.create_server(
        ("127.0.0.1", 0),
        stream,
        web.Route(
            "/img.png",
            web.Blob(
                img_data.getvalue(),
                "image/png",
            ),
        ),
        web.Route("/dir/", web.Dir(os.path.dirname(__file__))),
        web.middleware.Debug(),
    ) as httpd:
        host, port = httpd.server_address
        url = f"http://{host}:{port}"
        print(f"run at: {url}\npress Ctrl+C to stop")
        webbrowser.open(url)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        while True:
            stream.write((datetime.now().isoformat() + "\n").encode("utf-8"))
            time.sleep(0.5)
