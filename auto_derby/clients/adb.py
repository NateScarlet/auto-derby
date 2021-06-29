# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


from pathlib import Path
from typing import Text, Tuple

import PIL.Image
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from .client import Client

import re

import logging
import time

LOGGER = logging.getLogger(__name__)


class ADBClient(Client):
    key_path: Text = "adb.local.key"

    def __init__(self, address: Text):
        hostname, port = address.split(":", 2)
        assert hostname, "invalid address: missing hostname: %s" % address
        assert port, "invalid port: missing port: %s" % address

        self.hostname = hostname
        self.port = int(port)
        self.device = AdbDeviceTcp(self.hostname, self.port)
        self._height, self._width = 0, 0

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
        time.sleep(0.5)

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

    def setup(self) -> None:
        self.connect()
        self.load_size()
        self.start_game()

    def screenshot(self) -> PIL.Image.Image:
        # img_data = self.device.shell(
        #     f"screencap -p",
        #     decode=False,
        #     transport_timeout_s=None,
        # )
        # img = PIL.Image.open(io.BytesIO(img_data))

        # TODO: compare with png format screenshot
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

    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float
    ) -> None:
        x1, y1 = point
        x2, y2 = x1 + dx, y1 + dy
        duration_ms = int(duration * 1e3)
        duration_ms = max(200, duration_ms)  # not work if too fast
        command = f"input swipe {x1} {y1} {x2} {y2} {duration_ms}"
        LOGGER.debug("swipe: %s", command)
        res = self.device.shell(
            command,
            read_timeout_s=10 + duration,
        )
        assert not res, res
        time.sleep(0.5)
