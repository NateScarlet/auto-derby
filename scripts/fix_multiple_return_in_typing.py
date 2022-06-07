# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: word Decomp Meanshift

from typing import Text
import re


def fix_multiple_return(line: Text) -> Text:
    if "def" not in line:
        return line
    match = re.match(r"(.*)-> ((?:[^,\[\]]+,)+ [^,\[\]]+):$", line)
    if not match:
        return line

    return f"{match.group(1)}-> Tuple[{match.group(2)}]:\n"


import argparse


def main():
    test1 = fix_multiple_return(
        "    def detectMultiScale(self, img, hitThreshold=..., winStride=..., padding=..., scale=..., finalThreshold=..., useMeanshiftGrouping=...) -> foundLocations, foundWeights:\n"
    )
    assert (
        test1
        == "    def detectMultiScale(self, img, hitThreshold=..., winStride=..., padding=..., scale=..., finalThreshold=..., useMeanshiftGrouping=...) -> Tuple[foundLocations, foundWeights]:\n"
    ), test1
    test2 = fix_multiple_return(
        "def SVDecomp(src, w=..., u=..., vt=..., flags=...) -> w, u, vt:\n"
    )
    assert (
        test2
        == "def SVDecomp(src, w=..., u=..., vt=..., flags=...) -> Tuple[w, u, vt]:\n"
    ), test2

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    p: Text = args.path
    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = [fix_multiple_return(i) for i in lines]
    with open(p, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)


if __name__ == "__main__":
    main()
