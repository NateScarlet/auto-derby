# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import logging


if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse

import PIL.Image
from auto_derby import app
from auto_derby.single_mode import Context
from auto_derby.scenes.single_mode import RaceMenuScene
from auto_derby.infrastructure.image_device_service import ImageDeviceService
from auto_derby.infrastructure.web_log_service import WebLogService


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("image", default="debug/last_screenshot.png")
    parser.add_argument("-s", "--scenario", default="ura")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        app.log = WebLogService(
            app.cleanup,
            buffer_path=":memory:",
        )

    with app.cleanup:
        image_path = args.image
        scenario = {
            "ura": Context.SCENARIO_URA,
            "aoharu": Context.SCENARIO_AOHARU,
            "climax": Context.SCENARIO_CLIMAX,
        }.get(args.scenario, args.scenario)
        image = PIL.Image.open(image_path)
        app.device = ImageDeviceService(image)
        ctx = Context.new()
        ctx.scenario = scenario
        for course, pos in RaceMenuScene().visible_courses(ctx):
            print(course, pos)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    main()
