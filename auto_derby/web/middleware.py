# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import os
from typing import Sequence, Text

from http import HTTPStatus
from .context import Context
import mimetypes

from .handler import Middleware, Handler

import traceback


class StaticFile(Middleware):
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
        with open(self.path, "rb") as f:
            ctx.send_file(HTTPStatus.OK, f)


class Route(Middleware):
    def __init__(
        self, path: Text, inner: Middleware, methods: Sequence[Text] = ()
    ) -> None:
        super().__init__()
        self.path = path
        self.methods = methods
        self.inner = inner

    def handle(self, ctx: Context, next: Handler) -> None:
        if ctx.path != self.path:
            return next(ctx)
        if self.methods and ctx.method not in self.methods:
            return next(ctx)

        self.inner.handle(ctx, next)


class Debug(Middleware):
    def handle(self, ctx: Context, next: Handler) -> None:
        try:
            next(ctx)
        except:
            ctx.send_text(HTTPStatus.INTERNAL_SERVER_ERROR, traceback.format_exc())
