# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import os


import sys

import subprocess
import shutil


def main():
    command = ["pyright"] if shutil.which("pyright") else ["npx", "pyright"]
    subprocess.call(
        command,
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
