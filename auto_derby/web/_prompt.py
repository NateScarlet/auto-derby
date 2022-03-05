# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import http
import http.server
import logging
import webbrowser
from typing import Any, Dict, Optional, Protocol, Text

import win32api
import win32con

from . import handler
from .context import Context

_LOGGER = logging.getLogger(__name__)


class _PromptMiddleware(handler.Middleware):
    def __init__(self, html: Text):
        self.html = html
        self.data: Dict[Any, Any] = {}

    def handle(self, ctx: Context, next: handler.Handler) -> None:
        if ctx.method == "GET":
            ctx.send_html(http.HTTPStatus.OK, self.html)
        elif ctx.method == "POST":
            self.data = ctx.form_data()
            ctx.send_html(
                http.HTTPStatus.OK,
                """\
<h1>done</h1>
<p>this page can be closed.</p>
""",
            )
            ctx.request_server_shutdown()
        else:
            next(ctx)


class Webview(Protocol):
    def open(self, url: Text) -> None:
        ...

    def shutdown(self) -> None:
        ...


class _DefaultWebview(Webview):
    def __init__(self) -> None:
        super().__init__()

    def open(self, url: Text):
        webbrowser.open(url)

    def shutdown(self) -> None:
        # press Ctrl+W
        VK_W = int.from_bytes(b'W', 'big')
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(VK_W, 0, 0, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_W, 0, win32con.KEYEVENTF_KEYUP, 0)


class NoOpWebview(Webview):
    def open(self, url: Text) -> None:
        pass

    def shutdown(self) -> None:
        pass


class g:
    default_webview = _DefaultWebview()


def prompt(
    html: Text,
    *middlewares: handler.Middleware,
    host: str = "127.0.0.1",
    port: int = 0,
    webview: Optional[Webview] = None,
) -> Dict[Any, Any]:
    webview = webview or g.default_webview
    pm = _PromptMiddleware(html)
    h = handler.from_middlewares((pm,) + middlewares)
    with http.server.ThreadingHTTPServer(
        (host, port), handler.to_http_handler_class(h)
    ) as httpd:
        host, port = httpd.server_address
        url = f"http://{host}:{port}"
        webview.open(url)
        _LOGGER.info(f"temporary server at: {url}")
        httpd.serve_forever()
    webview.shutdown()
    _LOGGER.info("form data: %s", pm.data)
    return pm.data
