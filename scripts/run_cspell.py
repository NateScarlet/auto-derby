# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations


import subprocess
import shutil


def main():
    command = ["cspell"] if shutil.which("cspell") else ["npx", "cspell"]
    subprocess.call(
        [*command, "--gitignore", "--no-progress", "**/*.{py,vue,ts}"],
        shell=True,
    )


if __name__ == "__main__":
    main()
