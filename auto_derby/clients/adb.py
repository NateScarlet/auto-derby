# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import io
import logging
import re
import time
from pathlib import Path
from typing import Callable, List, Text, Tuple

import PIL.Image
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from .client import Client

LOGGER = logging.getLogger(__name__)


class ADBClient(Client):
    key_path: Text = "adb.local.key"
    action_wait = 1

    def __init__(self, address: Text):
        hostname, port = address.split(":", 2)
        assert hostname, "invalid address: missing hostname: %s" % address
        assert port, "invalid port: missing port: %s" % address

        self.hostname = hostname
        self.port = int(port)
        self.device = AdbDeviceTcp(self.hostname, self.port)
        self._height, self._width = 0, 0
        self._screenshot = self._screenshot_init

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def connect(self):
        if not Path(ADBClient.key_path).exists():
            keygen(self.key_path)
        signer = PythonRSASigner.FromRSAKeyPath(self.key_path)
        self.device.connect(rsa_keys=[signer])

    def tap(self, point: Tuple[int, int]) -> None:
        x, y = point
        command = f"input tap {x} {y}"
        LOGGER.debug("tap: %s", command)
        res = self.device.shell(command)
        assert not res, res
        time.sleep(self.action_wait)

    def start_game(self):
        self.device.shell(
            "am start -n jp.co.cygames.umamusume/jp.co.cygames.umamusume_activity.UmamusumeActivity"
        )

    def load_size(self):
        res = self.device.shell("wm size")
        match = re.match(r"Physical size: (\d+)x(\d+)", res)
        assert match, "unexpected command result: %s" % res
        self._width = int(match.group(2))
        self._height = int(match.group(1))
        if self._width > self._height:
            # handle orientation
            self._height, self._width = self._width, self._height
        LOGGER.debug("screen size: width=%d height=%d", self.width, self.height)

    def _screenshot_init(self) -> PIL.Image.Image:
        screenshot_perf: List[Tuple[Callable[[], PIL.Image.Image], int]] = []
        for screenshot_method in (
            self._screenshot_raw,
            self._screenshot_png,
        ):
            start_counter_ns = time.perf_counter_ns()
            img = screenshot_method()
            perf_counter_ns = time.perf_counter_ns() - start_counter_ns
            extrema: Tuple[int, int] = img.convert("L").getextrema()  # type: ignore
            min_color, max_color = extrema
            is_constant = min_color == max_color
            LOGGER.debug(
                "screenshot method performance: name=%s perf_counter_ns=%d",
                screenshot_method.__name__,
                perf_counter_ns,
            )
            if is_constant:
                LOGGER.info(
                    "skip screenshot method that returns constant image: name=%s color=%s",
                    screenshot_method.__name__,
                    min_color,
                )
            else:
                screenshot_perf.append((screenshot_method, perf_counter_ns))
        if not screenshot_perf:
            raise RuntimeError("no screenshot method avaliable")
        screenshot_perf = sorted(screenshot_perf, key=lambda x: x[1])
        self._screenshot, perf = screenshot_perf[0]
        LOGGER.info(
            "selected screenshot method: name=%s perf_counter_ns=%d",
            self._screenshot.__name__,
            perf,
        )
        return self._screenshot()

    def _screenshot_png(self) -> PIL.Image.Image:
        img_data = self.device.shell(
            f"screencap -p",
            decode=False,
            transport_timeout_s=None,
        )
        img = PIL.Image.open(io.BytesIO(img_data))
        return img

    def _screenshot_raw(self) -> PIL.Image.Image:
        # https://stackoverflow.com/a/59470924
        img_data = self.device.shell(
            f"screencap",
            decode=False,
            transport_timeout_s=None,
        )
        width = int.from_bytes(img_data[0:4], "little")
        height = int.from_bytes(img_data[4:8], "little")
        pixel_format = int.from_bytes(img_data[8:12], "little")
        # https://developer.android.com/reference/android/graphics/PixelFormat#RGBA_8888
        assert pixel_format == 1, "unsupported pixel format: %s" % pixel_format
        img = PIL.Image.frombuffer(
            "RGBA", (width, height), img_data[12:], "raw", "RGBX", 0, 1
        ).convert("RGBA")
        return img

    def setup(self) -> None:
        self.connect()
        self.load_size()
        self.start_game()

    def screenshot(self) -> PIL.Image.Image:
        return self._screenshot()

    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        x1, y1 = point
        x2, y2 = x1 + dx, y1 + dy
        duration_ms = int(duration * 1e3)
        if duration_ms < 400:
            # not work if too fast
            dx = int(dx * 400 / duration_ms)
            dy = int(dy * 400 / duration_ms)
            duration_ms = 400
        command = f"input swipe {x1} {y1} {x2} {y2} {duration_ms}"
        LOGGER.debug("swipe: %s", command)
        res = self.device.shell(
            command,
            read_timeout_s=10 + duration,
        )
        assert not res, res
        time.sleep(self.action_wait)
