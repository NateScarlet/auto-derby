# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import http
import http.server
import logging
import os
import webbrowser
from typing import Any, Dict, Optional, Protocol, Text

from . import handler
from .context import Context

_LOGGER = logging.getLogger(__name__)


class _PromptMiddleware(handler.Middleware):
    def __init__(self, html: Text):
        self.html = html
        self.data: Dict[Any, Any] = {}

    def handle(self, ctx: Context, next: handler.Handler) -> None:
        if ctx.path != "/":
            return next(ctx)
        if ctx.method == "GET":
            ctx.set_header("Cache-Control", "no-store")
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
        self.url = ""

    def open(self, url: Text):
        self.url = url
        try:
            import win32gui

            self.h_wnd = win32gui.GetForegroundWindow()
        except ImportError:
            self.h_wnd = 0
        webbrowser.open(url)

    def shutdown(self) -> None:
        if not self.url.startswith("http://127.0.0.1:"):
            return

        # press Ctrl+W
        try:
            import win32api
            import win32con
        except ImportError:
            _LOGGER.info(
                "`win32api`/`win32con` module not found, browser tab need to be closed manually"
            )
            return
        VK_W = int.from_bytes(b"W", "big")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(VK_W, 0, 0, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_W, 0, win32con.KEYEVENTF_KEYUP, 0)

        try:
            import win32gui

            if self.h_wnd:
                win32gui.SetForegroundWindow(self.h_wnd)
        except Exception:
            pass


class NoOpWebview(Webview):
    def open(self, url: Text) -> None:
        pass

    def shutdown(self) -> None:
        pass


class g:
    default_webview = _DefaultWebview()
    disabled = bool(os.getenv("CI"))
    default_port = 8300


def prompt(
    html: Text,
    *middlewares: handler.Middleware,
    host: str = "127.0.0.1",
    port: int = 0,
    max_port: int = 65535,
    webview: Optional[Webview] = None,
) -> Dict[Any, Any]:
    """the token can be set as query params `token` or header `Authorization: Bearer {token}`."""
    if g.disabled:
        return {}
    port = port or g.default_port
    webview = webview or g.default_webview
    pm = _PromptMiddleware(html)
    h = handler.from_middlewares((pm,) + middlewares)
    with http.server.ThreadingHTTPServer(
        (host, port),
        handler.to_http_handler_class(h),
        bind_and_activate=False,
    ) as httpd:
        httpd.allow_reuse_address = False
        while True:
            try:
                httpd.server_bind()
                break
            except OSError:
                if port >= max_port:
                    raise
                port += 1
                httpd.server_address = (httpd.server_address[0], port)
        httpd.server_activate()
        host, port = httpd.server_address
        url = f"http://{host}:{port}"
        webview.open(url)
        _LOGGER.info(f"prompt at: {url}")
        httpd.serve_forever()
    webview.shutdown()
    _LOGGER.info("form data: %s", pm.data)
    return pm.data
