# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import os
    import sys

    sys.path.insert(0, os.path.join(__file__, "../.."))


import argparse

import time
from auto_derby.infrastructure.web_log_service import WebLogService
import logging

_LOGGER = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--path", default="debug/log.jsonl")
    parser.add_argument(
        "--files",
        help="log files folder path, defaults to `./files` relative to log path",
    )
    parser.add_argument("--host", default=WebLogService.default_host)
    parser.add_argument("--port", type=int, default=WebLogService.default_port)
    args = parser.parse_args()
    path = args.path
    if args.files:
        files = args.files
    else:
        files = os.path.abspath(os.path.join(path, "../files"))
    s = WebLogService(
        host=args.host,
        port=args.port,
        buffer_path=path,
        image_path=files,
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
