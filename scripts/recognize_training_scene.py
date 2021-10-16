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
from auto_derby import single_mode, template, config
from auto_derby.single_mode import Context


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("image", default="debug/last_screenshot.png")
    parser.add_argument("-s", "--scenario", default="ura")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--debug-partner", action="store_true")
    args = parser.parse_args()
    if args.debug:
        os.environ["DEBUG"] = "auto_derby.single_mode.training.training"
    if args.debug_partner:
        os.environ["DEBUG"] = "auto_derby.single_mode.training.partner"
    if os.getenv("DEBUG", "").startswith("auto_derby.single_mode.training"):
        config.single_mode_training_image_path = "debug/recognize_training_scene"
        config.apply()
    for i in os.getenv("DEBUG", "").split(","):
        if not i:
            continue
        logging.getLogger(i).setLevel(logging.DEBUG)
    image_path = args.image
    scenario = {
        "ura": Context.SCENARIO_URA,
        "aoharu": Context.SCENARIO_AOHARU,
    }.get(args.scenario, args.scenario)
    image = PIL.Image.open(image_path)
    template.g.screenshot_width = image.width
    ctx = Context.new()
    ctx.scenario = scenario
    training = single_mode.Training.from_training_scene_v2(ctx, image)
    print(training)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    main()
