# -*- coding=UTF-8 -*-

# pyright: strict

from __future__ import annotations

import http.server
import http
from typing import Any, Dict, Text
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


def prompt(html: Text, *middlewares: handler.Middleware) -> Dict[Any, Any]:
    pm = _PromptMiddleware(html)
    h = handler.from_middlewares((pm,) + middlewares)
    with http.server.HTTPServer(
        ("127.0.0.1", 0), handler.to_http_handler_class(h)
    ) as httpd:
        host, port = httpd.server_address
        url = f"http://{host}:{port}"
        _LOGGER.info(f"temporary http server at: {url}")
        webbrowser.open(url)
        httpd.serve_forever()
    return pm.data
