# -*- coding=UTF-8 -*-
# pyright: strict

from typing import Text
import re


def _fix_outmost_bracket(v: Text) -> Text:
    assert v.startswith("[,")
    assert v.endswith("])")
    ret = v[2:-2] + ")"
    match = re.match(r"[^\[,\)]+", ret)
    assert match

    ret = f",{match.group(0)}=...{ret[match.end():]}"
    return ret


def fix_bracket(line: Text) -> Text:
    ret = line
    while True:
        try:
            match = next(re.finditer(r"\[,.+\]\)", ret))
            ret = (
                ret[: match.start()]
                + _fix_outmost_bracket(match.group(0))
                + ret[match.end() :]
            )
        except StopIteration:
            return ret.replace("(, ", "(")


import argparse


def main():
    test1 = fix_bracket(
        "    def create(backend[, maxTilt[, minTilt[, tiltStep[, rotateStepBase]]]]) -> retval:"
    )
    assert (
        test1
        == "    def create(backend, maxTilt=..., minTilt=..., tiltStep=..., rotateStepBase=...) -> retval:"
    ), test1

    test2 = fix_bracket(
        "    def create([, descriptor_type[, descriptor_size[, descriptor_channels[, threshold[, nOctaves[, nOctaveLayers[, diffusivity]]]]]]]) -> retval:"
    )
    assert (
        test2
        == "    def create(descriptor_type=..., descriptor_size=..., descriptor_channels=..., threshold=..., nOctaves=..., nOctaveLayers=..., diffusivity=...) -> retval:"
    ), test2

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    p: Text = args.path
    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = [fix_bracket(i) for i in lines]
    with open(p, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)


if __name__ == "__main__":
    main()
