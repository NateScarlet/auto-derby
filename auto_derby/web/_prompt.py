# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import http.server
import http
from typing import Any, Callable, Dict, Text
import webbrowser

import logging

_LOGGER = logging.getLogger(__name__)

from . import handler
from .context import Context


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


def _default_open_url(url: Text):
    webbrowser.open(url)


def prompt(
    html: Text,
    *middlewares: handler.Middleware,
    host: str = "127.0.0.1",
    port: int = 0,
    open_url: Callable[[Text], None] = _default_open_url,
) -> Dict[Any, Any]:
    pm = _PromptMiddleware(html)
    h = handler.from_middlewares((pm,) + middlewares)
    with http.server.HTTPServer(
        (host, port), handler.to_http_handler_class(h)
    ) as httpd:
        host, port = httpd.server_address
        url = f"http://{host}:{port}"
        _LOGGER.info(f"temporary server at: {url}")
        open_url(url)
        httpd.serve_forever()
    _LOGGER.info("form data: %s", pm.data)
    return pm.data
