# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import http
import http.server
import logging
import os
from typing import Any, Dict, Optional, Text
from . import handler
from .context import Context
from .webview import Webview, DefaultWebview

_LOGGER = logging.getLogger(__name__)


class _PromptMiddleware(handler.Middleware):
    def __init__(self, html: Text):
        self.html = html
        self.data: Dict[Any, Any] = {}

    def handle(self, ctx: Context, next: handler.Handler) -> None:
        if ctx.path != "/":
            return next(ctx)
        if ctx.method == "GET":
            # XXX: chrome memory cache not respect Cache-Control
            if "Chrome/" in ctx.request_headers.get(
                "User-Agent"
            ) and "memory_cache" not in ctx.params("prevent"):
                ctx.set_header(
                    "location",
                    "/?"
                    + (ctx.query + "&" if ctx.query else "")
                    + "prevent=memory_cache",
                )
                ctx.send_text(http.HTTPStatus.TEMPORARY_REDIRECT, "redirect")
                return
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


class g:
    default_webview = DefaultWebview()
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
