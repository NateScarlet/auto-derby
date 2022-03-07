# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from .context import Context


from http import HTTPStatus
from typing import Sequence, Text
from typing import Callable, Protocol
import http.server

Handler = Callable[[Context], None]


class Middleware(Protocol):
    def handle(self, ctx: Context, next: Handler) -> None:
        ...


def _apply_middleware(h: Handler, m: Middleware) -> Handler:
    def _handler(ctx: Context):
        m.handle(ctx, h)

    return _handler


def _default_handler(ctx: Context):
    if ctx.status_code:
        return
    ctx.send_text(HTTPStatus.NOT_FOUND, "404 page not found")


def from_middlewares(middlewares: Sequence[Middleware]) -> Handler:
    h = _default_handler
    for i in middlewares:
        h = _apply_middleware(h, i)
    return h


def to_http_handler_class(h: Handler, methods: Sequence[Text] = ()):
    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_HEAD(self):
            ctx = Context(self)
            h(ctx)
            ctx.end_headers()

        def do_GET(self):
            ctx = Context(self)
            h(ctx)
            ctx.end_write()

        do_POST = do_GET
        do_DELETE = do_GET
        do_PUT = do_GET

    return _Handler
