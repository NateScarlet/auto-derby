# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse

from auto_derby import clients, template


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dest",
        dest="dst",
        default="debug/last_screenshot.png",
    )

    args = parser.parse_args()
    dst = args.dst

    c = clients.DMMClient.find()
    if not c:
        raise RuntimeError("DMM client not running")
    c.setup()
    clients.set_current(c)
    template.g.last_screenshot_save_path = dst
    template.screenshot()


if __name__ == "__main__":
    main()
