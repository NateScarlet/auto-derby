# -*- coding=UTF-8 -*-
# pyright: strict

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../.."))


from typing import Text
import cv2
from auto_derby import template, templates, imagetools
import pathlib
import PIL.Image
import numpy as np
import argparse

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


def create_pos_mask(name: Text, game_img: PIL.Image.Image, threshold: float):
    template.g.screenshot_width = game_img.width
    pos_name = template.add_middle_ext(name, "pos")
    pos_img = template.try_load(pos_name)

    if pos_img:
        out_img = np.array(pos_img.convert("L"), dtype=np.uint8)
    else:
        out_img = np.zeros((game_img.height, game_img.width), dtype=np.uint8)

    padding = 2
    for _, pos in template.match(
        game_img, template.Specification(name, templates.ANY_POS, threshold=threshold)
    ):
        print(pos)
        x, y = pos
        out_img[y - padding : y + padding, x - padding : x + padding] = 255

    img = PIL.Image.fromarray(out_img).convert("1")
    dest = str(_TEMPLATES_PATH / template.add_middle_ext(name, "pos"))
    img.save(dest)
    cv2.imshow("out", out_img)
    cv2.waitKey()
    cv2.destroyWindow("out")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--name", "-n", dest="name")
    parser.add_argument(
        "--game-image", "-g", dest="game_image", default="last_screenshot.local.png"
    )
    parser.add_argument("--threshold", "-t", dest="threshold", type=float, default=0.9)
    args = parser.parse_args()
    name = args.name
    threshold = args.threshold
    game_image_path = args.game_image
    if not name:
        name = _latest_file()
    game_image = imagetools.resize(
        PIL.Image.open(game_image_path), width=template.TARGET_WIDTH
    )
    create_pos_mask(name, game_image, threshold)


if __name__ == "__main__":
    main()
