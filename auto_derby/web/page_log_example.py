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
import urllib.parse
import webbrowser
from typing import Tuple

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
        "source": "page_log_example",
        "msg": "this is a text message",
    }


def _sample_screenshot():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": "/files/screenshot.png",
        "caption": "this is a screenshot image ",
    }


def _sample_small_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": "/files/small.png",
        "caption": "this is a small image",
    }


def _sample_internet_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": "https://httpbin.org/image/png",
        "caption": "this is a internet image",
    }


def _sample_not_saved_image():
    _image_placeholder_svg_template = """\
<svg width="540" height="200" version="1.1" viewBox="0 0 143 53" xmlns="http://www.w3.org/2000/svg">
 <rect width="100%" height="100%" fill="#fff"/>
 <text font-family="sans-serif" font-size="10px"><tspan x="32" y="15">Image not saved</tspan></text>
 <text x="71" y="33" font-family="serif" font-size="5px" text-anchor="middle"><tspan x="71.4" y="33.1">reason:</tspan><tspan x="71.4" y="37.8">image save path not set</tspan><tspan x="71.4" y="42.6">and size greater than inline limit</tspan></text>
 <text x="42" y="25" font-family="sans-serif" font-size="6px"><tspan x="43.5" y="25.9">resolution={width}x{height}</tspan></text>
</svg>
"""
    svg = _image_placeholder_svg_template.format(
        width=540,
        height=950,
    )
    url = f"data:image/svg+xml,{urllib.parse.quote(svg)}"

    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": url,
        "caption": "this is a placeholder for not saved image",
    }


def _sample_small_layered_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": "/files/small.png",
        "layers": [
            {"name": "red", "url": "/files/small.red.png"},
            {"name": "green", "url": "/files/small.green.png"},
            {"name": "blue", "url": "/files/small.blue.png"},
        ],
        "caption": "this is a small image with layers",
    }


def _sample_large_layered_image():
    return {
        "ts": _ts(),
        "lv": _random_level(),
        "t": "IMAGE",
        "source": "page_log_example",
        "url": "/files/large.png",
        "layers": [
            {"name": "red", "url": "/files/large.red.png"},
            {"name": "green", "url": "/files/large.green.png"},
            {"name": "blue", "url": "/files/large.blue.png"},
        ],
        "caption": "this is a large image with layers",
    }


def _constant(size: Tuple[int, int], color: Tuple[int, int, int]):
    b = io.BytesIO()
    Image.new("RGB", size, color).save(b, "PNG")
    return web.Blob(b.getvalue(), "image/png")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    samples = [
        *([_sample_text] * 10),
        *([_sample_small_image] * 10),
        *[
            _sample_screenshot,
            _sample_not_saved_image,
            _sample_internet_image,
            _sample_screenshot,
            _sample_small_layered_image,
            _sample_large_layered_image,
        ],
    ]
    stream = web.Stream("", "text/plain")

    stop = threading.Event()

    def _run():
        with web.create_server(
            ("127.0.0.1", 8300),
            web.Blob(
                web.page.render(
                    {
                        "type": "LOG",
                        "streamURL": "/log",
                    }
                ).encode("utf-8"),
                "text/html; charset=utf-8",
            ),
            web.page.ASSETS,
            web.Path("/log", stream),
            web.Path(
                "/files/small.png",
                _constant((150, 16), (255, 255, 255)),
            ),
            web.Path(
                "/files/small.red.png",
                _constant((150, 16), (255, 0, 0)),
            ),
            web.Path(
                "/files/small.green.png",
                _constant((150, 16), (0, 255, 0)),
            ),
            web.Path(
                "/files/small.blue.png",
                _constant((150, 16), (0, 0, 255)),
            ),
            web.Path(
                "/files/screenshot.png",
                _constant((540, 960), (0, 255, 0)),
            ),
            web.Path(
                "/files/large.png",
                _constant((540, 960), (255, 255, 255)),
            ),
            web.Path(
                "/files/large.red.png",
                _constant((540, 960), (255, 0, 0)),
            ),
            web.Path(
                "/files/large.green.png",
                _constant((540, 960), (0, 255, 0)),
            ),
            web.Path(
                "/files/large.blue.png",
                _constant((540, 960), (0, 0, 255)),
            ),
            web.Route("/dir/", web.Dir(os.path.dirname(__file__))),
            web.middleware.Debug(),
        ) as httpd:

            def _cleanup():
                stop.wait()
                stream.close()
                httpd.shutdown()

            threading.Thread(target=_cleanup).start()
            host, port = httpd.server_address
            url = f"http://{host}:{port}"
            print(f"run at: {url}\npress Ctrl+C to stop")
            webbrowser.open(url)
            httpd.serve_forever()

    threading.Thread(target=_run).start()
    try:
        while True:
            # if not random.randint(0, 20):
            #     stream.write("bad value\n".encode("utf-8"))
            sample = json.dumps(random.choice(samples)())
            stream.write((sample + "\n").encode("utf-8"))
            time.sleep(0.5)
    finally:
        stop.set()
