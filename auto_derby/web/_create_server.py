# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import http.server
from . import handler


def create_server(
    *middlewares: handler.Middleware,
    host: str,
    port: int,
    max_port: int = 65535,
) -> http.server.HTTPServer:
    h = handler.from_middlewares(middlewares)
    httpd = http.server.ThreadingHTTPServer(
        (host, port),
        handler.to_http_handler_class(h),
        bind_and_activate=False,
    )
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
    return httpd
