# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))

import datetime
import io
import json
import logging
import random
import threading
import time
import webbrowser

from PIL import Image

import web


def _ts():
    return datetime.datetime.now().astimezone().isoformat()


def _random_level():
    return random.choice(("DEBUG", "INFO", "WARN", "ERROR"))


def _sample_text():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "TEXT",
        "msg": "this is a text message",
    }


def _sample_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "url": "/files/img.png",
        "caption": "this is a image message",
    }


def _sample_image2():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "url": "https://httpbin.org/image/png",
        "caption": "this is a image message",
    }


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    img_data = io.BytesIO()
    Image.new("RGB", (200, 200), (255, 0, 0)).save(img_data, "PNG"),
    samples = [_sample_text] * 10 + [
        _sample_image,
        _sample_image2,
    ]
    with web.Stream("", "text/plain") as stream, web.create_server(
        ("127.0.0.1", 8300),
        web.Blob(
            web.page.render(
                {
                    "type": "LOG",
                    "streamURL": "/stream",
                }
            ).encode("utf-8"),
            "text/html; charset=utf-8",
        ),
        web.page.ASSETS,
        web.Path("/stream", stream),
        web.Path(
            "/files/img.png",
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
            if not random.randint(0, 20):
                stream.write("bad value\n".encode("utf-8"))
            sample = json.dumps(random.choice(samples)())
            stream.write((sample + "\n").encode("utf-8"))
            time.sleep(0.5)
