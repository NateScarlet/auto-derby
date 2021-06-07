# -*- coding=UTF-8 -*-
"""Show help for everything in a module, not only visible items.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import pydoc
import re
import importlib


def indent(lines, prefix="    "):
    for i in lines:
        yield prefix + i


def full_help(module):
    placeholder = object()
    orig_all = getattr(module, "__all__", placeholder)

    module.__all__ = dir(module)
    try:
        # pydoc is using backspace to bold output
        # https://stackoverflow.com/questions/6827011/decoding-a-string-in-python-with-x08-x08-d-x08de-x08el-x08li-x08it-x08te
        return re.sub(r".\x08", "", pydoc.TextDoc().docmodule(module))
    finally:
        if orig_all is placeholder:
            del module.__all__
        else:
            module.__all__ = orig_all


if __name__ == "__main__":
    import argparse
    import importlib

    parser = argparse.ArgumentParser()
    parser.add_argument("import_name", nargs="+")
    args = parser.parse_args()

    for i in args.import_name:
        sys.stdout.write(full_help(importlib.import_module(i)))
