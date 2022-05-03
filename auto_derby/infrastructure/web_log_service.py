# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import os
import threading
import traceback
import urllib.parse
import webbrowser
from datetime import datetime
from typing import Any, Dict, Optional, Text, Tuple

import PIL.Image

from .. import imagetools, web
from ..services.cleanup import Service as Cleanup
from ..services.log import Image, Level, Service
from ..web import Webview

_LOGGER = logging.getLogger(__name__)


class _DefaultWebview(Webview):
    def open(self, url: Text) -> None:
        webbrowser.open(url)

    def shutdown(self) -> None:
        pass


def _image_data_url(img: PIL.Image.Image) -> Text:
    b = io.BytesIO()
    img.save(b, "PNG")
    data = base64.b64encode(b.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{data}"


class WebLogService(Service):
    _infra_module_prefix = ".".join(__name__.split(".")[:-1]) + "."
    _image_placeholder_svg_template = """\
<svg width="540" height="200" version="1.1" viewBox="0 0 143 53" xmlns="http://www.w3.org/2000/svg">
 <rect width="100%" height="100%" fill="#fff"/>
 <text font-family="sans-serif" font-size="10px"><tspan x="32" y="15">Image not saved</tspan></text>
 <text x="71" y="33" font-family="serif" font-size="5px" text-anchor="middle"><tspan x="71.4" y="33.1">reason:</tspan><tspan x="71.4" y="37.8">image save path not set</tspan><tspan x="71.4" y="42.6">and size greater than inline limit</tspan></text>
 <text x="42" y="25" font-family="sans-serif" font-size="6px"><tspan x="43.5" y="25.9">resolution={width}x{height}</tspan></text>
</svg>
"""

    default_webview: Webview = _DefaultWebview()
    default_port = 8400
    default_host = "127.0.0.1"
    default_buffer_path = ""
    default_image_path = ""
    max_inline_image_pixels = 5000

    def __init__(
        self,
        cleanup: Cleanup,
        host: Optional[Text] = None,
        port: Optional[int] = None,
        webview: Optional[web.Webview] = None,
        buffer_path: Optional[Text] = None,
        image_path: Optional[Text] = None,
    ) -> None:
        if host is None:
            host = self.default_host
        if port is None:
            port = self.default_port
        if webview is None:
            webview = self.default_webview
        if buffer_path is None:
            buffer_path = self.default_buffer_path
        if image_path is None:
            image_path = self.default_image_path
        self.image_path = image_path
        self._always_inline_image = not buffer_path

        self._s = web.Stream(buffer_path, "text/plain; charset=utf-8")
        self._stop = threading.Event()

        def _run(address: Tuple[Text, int]):
            with self._s, web.create_server(
                address,
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
                web.Path("/log", self._s),
                web.Route("/images/", web.Dir(self.image_path)),
            ) as httpd:

                def _on_stop():
                    self._stop.wait()
                    self._s.close()
                    httpd.shutdown()

                threading.Thread(target=_on_stop).start()
                host, port = httpd.server_address
                url = f"http://{host}:{port}"
                _LOGGER.info("web log service start at:\t%s", url)
                webview.open(url)
                httpd.serve_forever()

        threading.Thread(target=_run, args=((host, port),)).start()
        cleanup.add(self.stop)

    def close(self):
        self._s.close()

    def stop(self):
        self._stop.set()

    def __del__(self):
        self.close()
        self.stop()

    def _source(self) -> Text:
        stack_level = 0
        for f, lineno in traceback.walk_stack(None):
            stack_level += 1
            name = f.f_globals.get("__name__")
            if name and not name.startswith(self._infra_module_prefix):
                return f"{name}:{lineno}"
        return ""

    def _line(self, fields: Dict[Text, Any]):
        data = json.dumps(
            {
                "ts": datetime.now().astimezone().isoformat(),
                "lv": fields["lv"],
                "t": fields["t"],
                "source": self._source(),
                **fields,
            }
        ).encode("utf-8")
        self._s.write(data)
        self._s.write(b"\n")

    def _text(self, level: Level, msg: Text):
        self._line({"t": "TEXT", "lv": level.value, "msg": msg})

    def text(self, msg: Text, /, *, level: Level = Level.INFO):
        self._text(level, msg)

    def _image_url(self, image: Image) -> Text:
        pil_img = imagetools.pil_image_of(image)
        n_pixels = pil_img.width * pil_img.height
        if self._always_inline_image or n_pixels < self.max_inline_image_pixels:
            return _image_data_url(pil_img)
        if not self.image_path:
            svg = self._image_placeholder_svg_template.format(
                width=pil_img.width,
                height=pil_img.height,
            )
            return f"data:image/svg+xml,{urllib.parse.quote(svg)}"

        h = hashlib.md5(pil_img.tobytes()).hexdigest()
        pathname = f"{h[0]}/{h[1:3]}/{h[3:]}.png"
        dst = os.path.join(self.image_path, pathname)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        pil_img.save(dst)
        return "/images/" + pathname

    def image(
        self,
        caption: Text,
        image: Image,
        /,
        *,
        level: Level = Level.INFO,
        layers: Dict[Text, Image] = {},
    ):

        d = {
            "t": "IMAGE",
            "lv": level.value,
            "caption": caption,
            "url": self._image_url(image),
        }
        if layers:
            d["layers"] = [
                {"name": k, "url": self._image_url(v)} for k, v in layers.items()
            ]
        self._line(d)
