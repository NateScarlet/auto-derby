# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import os


import sys

import subprocess


def main():
    subprocess.call(
        ["npx", "pyright"],
        env={
            **os.environ,
            "PATH": os.path.pathsep.join(
                (
                    os.path.dirname(sys.executable),
                    os.getenv("PATH") or "",
                )
            ),
        },
        shell=True,
    )


if __name__ == "__main__":
    main()
