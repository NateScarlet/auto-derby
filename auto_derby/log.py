# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import logging
import traceback
from typing import Any, Callable, Dict, Protocol, Text, Union
from PIL.Image import Image
import numpy as np


class LogService(Protocol):
    def debug(self, msg: Text, data: Dict[Text, Any] = ..., /):
        ...

    def warn(self, msg: Text, data: Dict[Text, Any] = ..., /):
        ...

    def info(self, msg: Text, data: Dict[Text, Any] = ..., /):
        ...

    def error(self, msg: Text, data: Dict[Text, Any] = ..., /):
        ...

    def image(self, caption: Text, image: Union[Image, np.ndarray]):
        ...

    def image_url(self, caption: Text, url: Text, /):
        ...


class NoOpLogService(LogService):
    def debug(self, msg: Text, data: Dict[Text, Any] = ..., /):
        pass

    def warn(self, msg: Text, data: Dict[Text, Any] = ..., /):
        pass

    def info(self, msg: Text, data: Dict[Text, Any] = ..., /):
        pass

    def error(self, msg: Text, data: Dict[Text, Any] = ..., /):
        pass

    def image(self, caption: Text, image: Union[Image, np.ndarray]):
        pass

    def image_url(self, caption: Text, url: Text, /):
        pass


class LogServiceHandler(logging.Handler):
    def __init__(self, service: LogService, /) -> None:
        super().__init__()
        self._s = service

    def _record_data(self, record: logging.LogRecord) -> Dict[Text, Any]:
        d = {
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        if record.exc_text:
            d["error"] = record.exc_text
        if record.exc_info:
            d["traceback"] = "\n".join(traceback.format_exception(*record.exc_info))
        return d

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno == logging.DEBUG:
            self._s.debug(record.getMessage(), self._record_data(record))
        if record.levelno == logging.INFO:
            self._s.info(record.getMessage(), self._record_data(record))
        if record.levelno == logging.WARNING:
            self._s.warn(record.getMessage(), self._record_data(record))
        if record.levelno == logging.ERROR:
            self._s.error(record.getMessage(), self._record_data(record))


class DynamicLogServiceHandler(LogServiceHandler):
    def __init__(self, service: Callable[[], LogService], /) -> None:
        super(LogServiceHandler, self).__init__()
        self._s_getter = service

    @property
    def _s(self):
        return self._s_getter()
