# -*- coding=UTF-8 -*-
# pyright: strict

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse
import pathlib
from typing import Text

import cv2
import numpy as np
import PIL.Image
from auto_derby import app, imagetools, template, templates
from auto_derby.infrastructure.image_device_service import ImageDeviceService

_TEMPLATES_PATH = pathlib.Path(templates.__file__).parent


def _all_templates():
    for i in _TEMPLATES_PATH.glob("*.png"):
        if i.is_dir():
            continue
        if str(i).endswith(".pos.png"):
            continue
        yield i


def _latest_file():
    return str(
        (sorted(_all_templates(), key=lambda x: x.stat().st_mtime, reverse=True))[
            0
        ].name
    )


def create_pos_mask(
    name: Text,
    game_img: PIL.Image.Image,
    threshold: float,
    padding: int,
):
    app.device = ImageDeviceService(game_img)
    pos_name = template.add_middle_ext(name, "pos")
    pos_img = template.try_load(pos_name)

    if pos_img:
        out_img = np.array(pos_img.convert("L"), dtype=np.uint8)
    else:
        out_img = np.zeros((960, 540), dtype=np.uint8)

    for _, pos in template.match(
        game_img, template.Specification(name, templates.ANY_POS, threshold=threshold)
    ):
        print(pos)
        x, y = pos
        out_img[y - padding : y + padding, x - padding : x + padding] = 255

    cv2.imshow("out", out_img)
    cv2.waitKey()
    cv2.destroyWindow("out")
    return PIL.Image.fromarray(out_img).convert("1")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--name", "-n", dest="name")
    parser.add_argument(
        "--game-image", "-g", dest="game_image", default="debug/last_screenshot.png"
    )
    parser.add_argument("--threshold", "-t", dest="threshold", type=float, default=0.9)
    parser.add_argument("--padding", "-p", dest="padding", type=int, default=2)
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--no-save", dest="no_save", action="store_true")
    args = parser.parse_args()
    name = args.name
    if args.debug:
        template._DEBUG_TMPL = name  # type: ignore
    threshold = args.threshold
    padding = args.padding
    game_image_path = args.game_image
    if not name:
        name = _latest_file()
    game_image = imagetools.resize(
        PIL.Image.open(game_image_path), width=template.TARGET_WIDTH
    )
    img = create_pos_mask(name, game_image, threshold, padding)

    if args.no_save:
        return
    dest = (_TEMPLATES_PATH / template.add_middle_ext(name, "pos")).resolve()
    img.save(dest)
    print(dest.name)


if __name__ == "__main__":
    main()
