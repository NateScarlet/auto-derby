import contextlib
import http.server
import io
from msilib.schema import Binary
import shutil
import threading
from typing import BinaryIO, Callable, List, Optional, Protocol, Text


from .middleware import Middleware
from .context import Context
from .handler import Handler, Middleware
from . import handler

import queue


class StreamWriter(Protocol):
    def write(self, data: bytes) -> None:
        ...

    def close(self) -> None:
        ...

    def closed(self) -> bool:
        ...


class FileStreamWriter(StreamWriter):
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

    def copy_to(self, w: StreamWriter):
        if not self.path:
            return
        with self._lock:
            with open(self.path, "rb") as f:
                shutil.copyfileobj(f, w)


class QueueWriter(StreamWriter):
    def __init__(self) -> None:
        self._q: queue.Queue[bytes] = queue.Queue()
        self._closed = False

    def write(self, data: bytes) -> None:
        self._q.put(data)

    def close(self) -> None:
        self._closed = True

    def closed(self) -> bool:
        return self._closed

    def get(self) -> bytes:
        return self._q.get()


class ResponseStreamWriter(StreamWriter):
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def write(self, data: bytes) -> None:
        self._ctx.write_bytes(data)

    def close(self) -> None:
        self._ctx.end_write()

    def closed(self) -> bool:
        return self._ctx.writer_closed()


class _Stream(Middleware):
    def __init__(
        self, buffer_path: Text, mimetype: Text = "application/octet-stream"
    ) -> None:
        self._f = FileStreamWriter(buffer_path)
        self._lock = threading.Lock()
        self._writers: List[StreamWriter] = [self._f]
        self._closed = False
        self._mimetype = mimetype
        self.on_close: Callable[[], None] = lambda: None

    def handle(self, ctx: Context, next: Handler) -> None:
        with self._lock:
            if self._closed:
                return ctx.send_text(200, "stream closed")

        ctx.status_code = 200
        ctx.set_header("Content-Type", self._mimetype)
        ctx.start_stream()
        with contextlib.closing(QueueWriter()) as w:
            with self._lock:
                self._writers.append(w)
            self._f.copy_to(ResponseStreamWriter(ctx))
            while not w.closed():
                ctx.write_bytes(w.get())

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


from ._prompt import prompt, Webview
from . import _prompt
import logging

_LOGGER = logging.getLogger(__name__)


def stream(
    html: Text,
    *middlewares: Middleware,
    host: str = "127.0.0.1",
    port: int = 0,
    max_port: int = 65535,
    webview: Optional[Webview] = None,
    buffer_path: Text = "",
) -> StreamWriter:
    s = _Stream(buffer_path)
    host_arg = host
    port_arg = port or (_prompt.g.default_port - 1)
    webview = webview or _prompt.g.default_webview

    def _run():
        h = handler.from_middlewares((s,) + middlewares)
        host = host_arg
        port = port_arg
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
            # webview.open(url)
            _LOGGER.info(f"stream at: {url}")
            s.on_close = httpd.shutdown
            httpd.serve_forever()

    threading.Thread(target=_run, daemon=True).start()

    return s
