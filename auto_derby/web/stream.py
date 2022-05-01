# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import contextlib
import queue
import shutil
import threading
from typing import Callable, List, Protocol, Text

from .context import Context
from .handler import Handler, Middleware
from .middleware import Middleware


class Writer(Protocol):
    def write(self, data: bytes) -> None:
        ...

    def close(self) -> None:
        ...

    def closed(self) -> bool:
        ...


class FileWriter(Writer):
    def __init__(self, path: Text) -> None:
        self.path = path
        self._lock = threading.Lock()

    def write(self, data: bytes) -> None:
        if not self.path:
            return
        with self._lock:
            with open(self.path, "ab") as f:
                f.write(data)

    def close(self) -> None:
        pass

    def closed(self) -> bool:
        return not self.path

    def copy_to(self, w: Writer):
        if not self.path:
            return
        with self._lock:
            try:
                with open(self.path, "rb") as f:
                    shutil.copyfileobj(f, w)
            except FileNotFoundError:
                pass


class QueueWriter(Writer):
    def __init__(self) -> None:
        self._q: queue.Queue[bytes] = queue.Queue()
        self._closed = False

    def write(self, data: bytes) -> None:
        if self._closed:
            raise ValueError("queue writer closed")
        self._q.put(data)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._q.put(b"")

    def closed(self) -> bool:
        return self._closed

    def get(self) -> bytes:
        return self._q.get()


class ResponseWriter(Writer):
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def write(self, data: bytes) -> None:
        self._ctx.write_bytes(data)

    def close(self) -> None:
        self._ctx.end_write()

    def closed(self) -> bool:
        return self._ctx.writer_closed()


class Stream(Middleware):
    def __init__(
        self,
        buffer_path: Text,
        mimetype: Text,
    ) -> None:
        self._f = FileWriter(buffer_path)
        self._lock = threading.Lock()
        self._writers: List[Writer] = [self._f]
        self._closed = False
        self._mimetype = mimetype
        self.on_close: Callable[[], None] = lambda: None

    def handle(self, ctx: Context, next: Handler) -> None:
        ctx.status_code = 200
        ctx.set_header("Content-Type", self._mimetype)
        ctx.start_stream()
        with contextlib.closing(ResponseWriter(ctx)) as w, contextlib.closing(
            QueueWriter()
        ) as q:
            self._f.copy_to(w)
            with self._lock:
                if self._closed:
                    q.close()
                else:
                    self._writers.append(q)
            while not q.closed():
                w.write(q.get())

    def close(self):
        with self._lock:
            self._closed = True
            for i in self._writers:
                i.close()
            self.on_close()

    def closed(self):
        return self._closed

    def write(self, data: bytes):
        has_closed_writer = False
        with self._lock:
            for i in self._writers:
                if i.closed():
                    has_closed_writer = True
                    continue
                i.write(data)
            if has_closed_writer:
                self._writers = [i for i in self._writers if not i.closed()]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
