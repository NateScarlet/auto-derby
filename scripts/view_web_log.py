# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse
import logging
import time

from auto_derby import app
from auto_derby.infrastructure.web_log_service import WebLogService


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--path", "-p", default="debug/log.jsonl")
    parser.add_argument(
        "--image-path",
        help="log image folder path, defaults to `./images` relative to log path",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8300)
    args = parser.parse_args()
    path = args.path
    if args.image_path:
        image_path = args.image_path
    else:
        image_path = os.path.abspath(os.path.join(path, "../images"))
    with app.cleanup as cleanup:
        s = WebLogService(
            cleanup,
            host=args.host,
            port=args.port,
            buffer_path=path,
            image_path=image_path,
        )
        s.close()
        print("press Ctrl+C to stop")
        while True:
            time.sleep(1000)  # serve forever


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        level=logging.INFO,
        datefmt="%H:%M:%S",
    )
    main()
