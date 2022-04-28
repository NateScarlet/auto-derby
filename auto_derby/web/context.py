# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from collections import defaultdict

import email.utils
import io
import json
import shutil
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Any, BinaryIO, DefaultDict, Dict, List, Text


class Context:
    def __init__(self, req: BaseHTTPRequestHandler):
        self._req = req
        self._req_body = io.BytesIO()
        self._res_body = io.BytesIO()
        self._res_headers: DefaultDict[Text, List[Text]] = defaultdict(lambda: [])

        self.request_headers = req.headers
        self.method = req.command
        (
            self.scheme,
            self.host,
            self.path,
            self.query,
            _,
        ) = urllib.parse.urlsplit(req.path)
        self._parsed_query: Dict[Text, List[Text]] = {}
        self.status_code = 0
        self.encoding = "utf-8"
        self.header_written = False
        self._is_stream = False
        self._write_ended = False

    def params(self, key: Text) -> List[Text]:
        if not self._parsed_query:
            self._parsed_query = urllib.parse.parse_qs(self.query)
        return self._parsed_query.get(key, [])

    def param(self, key: Text) -> Text:
        l = self.params(key)
        if l:
            return l[0]
        return ""

    def body(self) -> bytes:
        f = self._req.rfile
        w = self._req_body
        if not f.closed:
            cl = int(self.request_headers.get("Content-Length", "0"))
            w.write(f.read(int(cl)))
            f.close()
        return self._req_body.getvalue()

    def form_data(self):
        data = self.body()
        ret: Dict[Any, Any] = {}
        ct = self.request_headers["Content-Type"]
        if ct in ("application/json", "text/json"):
            o = json.loads(data)
            ret.update(o)
        elif ct in ("application/x-www-form-urlencoded",):
            o = urllib.parse.parse_qs(data.decode("utf-8"), strict_parsing=True)
            ret.update(o)
        else:
            raise NotImplementedError("request Content-Type not supported: %s" % ct)
        return ret

    def set_header(self, key: Text, value: Text):
        self._res_headers[key] = [value]

    def add_header(self, key: Text, value: Text):
        self._res_headers.setdefault(key, []).append(value)

    def end_headers(self):
        if self.header_written:
            return
        self._req.send_response(self.status_code)
        r = self._req
        for k, v in self._res_headers.items():
            for i in v:
                r.send_header(k, i)
        r.end_headers()
        self.header_written = True

    def start_stream(self):
        if "chunked" not in self._res_headers["Transfer-Encoding"]:
            self._res_headers["Transfer-Encoding"] += ["chunked"]
        self.end_headers()
        self._is_stream = True

    def _write_chunked(self, data: bytes):
        w = self._req.wfile
        w.write(b"%X\r\n" % len(data))
        w.write(data)
        w.write(b"\r\n")
        w.flush()

    def write_bytes(self, data: bytes):
        if self._is_stream:
            return self._write_chunked(data)
        self._res_body.write(data)

    def writer_closed(self):
        return self._req.wfile.closed

    def write_string(self, data: str):
        self.write_bytes(data.encode(self.encoding, "surrogateescape"))

    def write_file(self, f: BinaryIO):
        if self._is_stream:
            ctx = self

            class _Writer:
                def write(self, data: bytes):
                    ctx.write_bytes(data)

            shutil.copyfileobj(f, _Writer())
            return

        w = self._res_body
        if "Content-Length" in self._res_headers:
            self.end_headers()
            w = self._req.wfile
        shutil.copyfileobj(f, w)

    def end_write(self):
        if self._write_ended:
            return
        if self._req.wfile.closed:
            self._write_ended = True
            return
        if self._is_stream:
            self.write_bytes(b"")
        else:
            data = self._res_body.getvalue()
            self.set_header("Content-Length", str(len(data)))
            self.end_headers()
            w = self._req.wfile
            w.write(data)
        self._write_ended = True

    def send_blob(self, status_code: int, data: bytes):
        self.status_code = status_code
        self.write_bytes(data)
        self.end_write()

    def send_text(self, status_code: int, data: Text):
        self.status_code = status_code
        self.set_header("Content-Type", "text/plain; charset=%s" % self.encoding)
        self.write_string(data)
        self.end_write()

    def send_html(self, status_code: int, html: Text):
        self.status_code = status_code
        self.set_header("Content-Type", "text/html; charset=%s" % self.encoding)
        self.write_string(html)
        self.end_write()

    def send_file(self, status_code: int, f: BinaryIO):
        self.status_code = status_code
        if "Content-Type" not in self._res_headers:
            self.set_header("Content-Type", "application/octet-stream")
        self.write_file(f)
        self.end_write()

    def request_server_shutdown(self):
        threading.Thread(
            target=self._req.server.shutdown,
        ).start()

    def is_not_modified(self, mtime: float) -> bool:
        try:
            ts = email.utils.parsedate_to_datetime(
                self.request_headers["If-Modified-Since"]
            ).timestamp()
            return int(mtime) <= ts
        except (TypeError, IndexError, OverflowError, ValueError):
            pass

        return False
