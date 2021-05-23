# -*- coding=UTF-8 -*-
# pyright: strict

if True:
    import sys
    import os
    sys.path.insert(0, os.path.join(__file__, "../.."), )


from typing import Text
import cv2
from auto_derby import window, template, templates
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
    return str((sorted(_all_templates(), key=lambda x: x.stat().st_mtime, reverse=True))[0].name)


def create_pos_mask(name: Text):

    game_img = template.screenshot(window.get_game())
    match_img = template.load(name)
    match = template.match(game_img, name)
    last_match = template.DEBUG_DATA["last_match"]
    if last_match is None:
        raise ValueError("missing debug data")

    out_img = np.zeros((game_img.height, game_img.width), dtype=float)

    if not match:
        raise ValueError("no match on screen")
    _, pos = match
    x, y = pos
    cv2.rectangle(out_img, pos, (x+match_img.width,
                                    y+match_img.height), (255,), -1)

    img = PIL.Image.fromarray(out_img).convert("1")
    dest = str(_TEMPLATES_PATH / template.add_middle_ext(name, "pos"))
    img.save(dest)
    cv2.imshow("out", out_img)
    cv2.waitKey()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--name", "-n", dest="name")
    args = parser.parse_args()
    name = args.name
    if not name:
        name = _latest_file()
    create_pos_mask(name)


if __name__ == '__main__':
    main()
