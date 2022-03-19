# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import mimetypes
import os
import traceback
from http import HTTPStatus
from typing import Sequence, Text

import email.utils
from .context import Context
from .handler import Handler, Middleware


class Blob(Middleware):
    def __init__(self, data: bytes, mimetype: Text = "") -> None:
        super().__init__()
        self.data = data
        self.mimetype = mimetype

    def handle(self, ctx: Context, next: Handler) -> None:
        if self.mimetype:
            ctx.set_header("Content-Type", self.mimetype)
        ctx.send_blob(HTTPStatus.OK, self.data)


class File(Middleware):
    def __init__(self, path: Text, mimetype: Text = "") -> None:
        super().__init__()
        self.path = path
        mt = mimetype
        if not mt:
            mt = mimetypes.types_map.get(os.path.splitext(path)[1]) or mt
        self.mimetype = mt

    def handle(self, ctx: Context, next: Handler) -> None:
        if self.mimetype:
            ctx.set_header("Content-Type", self.mimetype)
        try:
            stat = os.stat(self.path)
            if ctx.is_not_modified(stat.st_mtime):
                ctx.status_code = HTTPStatus.NOT_MODIFIED
                return
            ctx.set_header("Content-Length", str(stat.st_size))
            ctx.set_header(
                "Last-Modified", email.utils.formatdate(stat.st_mtime, usegmt=True)
            )
        except FileNotFoundError:
            ctx.send_text(HTTPStatus.NOT_FOUND, "file not found")
            return

        with open(self.path, "rb") as f:
            ctx.send_file(HTTPStatus.OK, f)


class Dir(Middleware):
    def __init__(self, path: Text) -> None:
        super().__init__()
        self.path = path

    def handle(self, ctx: Context, next: Handler) -> None:
        File(os.path.join(self.path, ctx.path)).handle(ctx, next)


class Route(Middleware):
    def __init__(
        self, prefix: Text, inner: Middleware, methods: Sequence[Text] = ()
    ) -> None:
        super().__init__()
        self.prefix = prefix
        self.methods = methods
        self.inner = inner

    def handle(self, ctx: Context, next: Handler) -> None:
        if not ctx.path.startswith(self.prefix):
            return next(ctx)
        if self.methods and ctx.method not in self.methods:
            return next(ctx)

        raw_path = ctx.path
        ctx.path = ctx.path[len(self.prefix) :]
        try:
            self.inner.handle(ctx, next)
        except:
            ctx.path = raw_path
            raise


class Debug(Middleware):
    def handle(self, ctx: Context, next: Handler) -> None:
        print(ctx.method, ctx.path)
        try:
            next(ctx)
        except:
            ctx.send_text(HTTPStatus.INTERNAL_SERVER_ERROR, traceback.format_exc())


class TokenAuth(Middleware):
    def __init__(self, token: Text, methods: Sequence[Text] = ()) -> None:
        self.token = token
        self.methods = methods

    def handle(self, ctx: Context, next: Handler) -> None:
        if self.methods and ctx.method not in self.methods:
            return next(ctx)
        if (
            ctx.param("token") == self.token
            or ctx.request_headers.get("Authorization") == f"Bearer {self.token}"
        ):
            return next(ctx)
        ctx.send_text(HTTPStatus.UNAUTHORIZED, "unauthorized")
