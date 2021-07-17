# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import argparse

import io
from typing import Set, Text


def _iter_unique_lines(file: io.TextIOWrapper):
    existed_lines: Set[Text] = set()
    for line in file:
        if line in existed_lines:
            continue
        yield line
        existed_lines.add(line)


def _apply_on_file(filename: Text) -> None:
    with open(filename, "r", encoding="utf-8") as f:
        unique_lines = list(_iter_unique_lines(f))

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(unique_lines)


def main():
    parser = argparse.ArgumentParser(description="remove duplicated line in a file")
    parser.add_argument("file", nargs="+", help="filenames")

    args = parser.parse_args()

    for filename in args.file:
        _apply_on_file(filename)


if __name__ == "__main__":
    main()
