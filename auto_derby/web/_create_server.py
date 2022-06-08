# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import http.server
from typing import Tuple, Type
from . import handler


def create_server(
    address: Tuple[str, int],
    *middlewares: handler.Middleware,
    max_port: int = 65535,
    server_class: Type[http.server.HTTPServer] = http.server.ThreadingHTTPServer,
) -> http.server.HTTPServer:
    h = handler.from_middlewares(middlewares)
    httpd = server_class(
        address,
        handler.to_http_handler_class(h),
        bind_and_activate=False,
    )
    httpd.allow_reuse_address = False
    _, port = address
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
