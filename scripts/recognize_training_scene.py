# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse

import PIL.Image
from auto_derby import imagetools, single_mode, template


def recognize_training(img: PIL.Image.Image):
    training = single_mode.Training.from_training_scene(img)
    print(training)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("image", default="debug/last_screenshot.png")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        os.environ["DEBUG"] = "auto_derby.single_mode.training"
    image_path = args.image
    image = imagetools.resize(PIL.Image.open(image_path), width=template.TARGET_WIDTH)
    recognize_training(image)


if __name__ == "__main__":
    main()
