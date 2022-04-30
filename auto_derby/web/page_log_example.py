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


def _sample_screenshot():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "url": "/files/screenshot.png",
        "caption": "this is a screenshot image ",
    }


def _sample_small_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "url": "/files/small.png",
        "caption": "this is a small image",
    }


def _sample_internet_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "url": "https://httpbin.org/image/png",
        "caption": "this is a internet image",
    }


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    small_image = io.BytesIO()
    Image.new("RGB", (150, 16), (255, 0, 0)).save(small_image, "PNG"),
    screenshot_image = io.BytesIO()
    Image.new("RGB", (540, 960), (0, 255, 0)).save(screenshot_image, "PNG"),
    samples = (
        [_sample_text] * 10
        + [_sample_small_image] * 10
        + [
            _sample_screenshot,
            _sample_internet_image,
            _sample_screenshot,
        ]
    )
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
            "/files/small.png",
            web.Blob(
                small_image.getvalue(),
                "image/png",
            ),
        ),
        web.Path(
            "/files/screenshot.png",
            web.Blob(
                screenshot_image.getvalue(),
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
