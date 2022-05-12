# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import http.server
from http import HTTPStatus
from typing import Any, Callable, Protocol, Sequence, Text

from .context import Context
from .. import app

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
        protocol_version = "HTTP/1.1"

        def handle(self) -> None:
            try:
                return super().handle()
            except ValueError as ex:
                if "readline of closed file" in str(ex):
                    pass
                else:
                    raise
            except (ConnectionAbortedError, ConnectionResetError):
                pass

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

        def log_error(self, format: str, *args: Any) -> None:
            app.log.text(format % args, level=app.ERROR)

        def log_message(self, format: str, *args: Any) -> None:
            app.log.text(format % args)

    return _Handler
