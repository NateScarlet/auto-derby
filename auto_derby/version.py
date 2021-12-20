# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words IDYES

from __future__ import annotations

import http.client
import urllib.request
import webbrowser
from typing import Text, Tuple

import cast_unknown as cast
import win32con

from . import window
from .__version__ import VERSION
from concurrent import futures
import logging

_LOGGER = logging.getLogger(__name__)


_VERSION_URLS = (
    "https://cdn.jsdelivr.net/gh/NateScarlet/auto-derby@master/version",
    "https://github.com/NateScarlet/auto-derby/raw/master/version",
    "https://natescarlet.coding.net/p/github/d/auto-derby/git/raw/master/version",
)
_CHANGELOG_URL = "https://github.com/NateScarlet/auto-derby/blob/master/CHANGELOG.md"


def _http_get(url: Text) -> Text:
    # Use `requests` if we have more http related feature
    resp = cast.instance(
        urllib.request.urlopen(url),
        http.client.HTTPResponse,
    )
    if resp.status != 200:
        raise RuntimeError("response status %d: %s", resp.status, url)
    return cast.text(resp.read())


def latest() -> Text:
    pool = futures.ThreadPoolExecutor()

    def _do(url: Text):
        return url, _http_get(url)

    jobs = [pool.submit(_do, url) for url in _VERSION_URLS]
    try:
        while jobs:
            try:
                done, jobs = futures.wait(jobs, return_when=futures.FIRST_COMPLETED)
                url, ret = done.pop().result()
                _LOGGER.info("lastest: %s from %s", ret, url)
                return ret
            except:
                pass
    finally:
        pool.shutdown(False)
    _LOGGER.warning("latest: all request failed, use current version")
    return VERSION


def parse(v: Text) -> Tuple[int, int, int, Text]:
    main, *extras = v.split("-")
    if main.count(".") != 2:
        return 0, 0, 0, v
    if main.startswith("v"):
        main = main[1:]
    extra = "-".join(extras)
    major, minor, patch = main.split(".")
    return int(major), int(minor), int(patch), extra


def check_update() -> None:
    latest_version = latest()
    if parse(latest_version) <= parse(VERSION):
        return

    def on_close(res: int):
        if res != win32con.IDYES:
            return
        webbrowser.open(_CHANGELOG_URL)

    window.message_box(
        f"New version available: {latest_version}\n" "open changelog in browser?",
        "auto-derby",
        flags=win32con.MB_YESNO,
        on_close=on_close,
    )
