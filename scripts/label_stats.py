# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words chara inout
"""show label stats.  """


if True:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import csv
import itertools
from collections import Counter
from typing import Iterator, Text, Tuple

from auto_derby import config, data
from auto_derby.single_mode import item


def _iter_item_labels(path: Text):
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        for k, v in csv.reader(f):
            yield k, int(v)


def _item_stats(labels: Iterator[Tuple[Text, int]]):
    values = Counter(i[1] for i in labels)
    for k, v in sorted(values.items(), key=lambda x: (-x[1], x[0])):
        yield "%4d\t%s" % (v, item.game_data.get(k))
    for i in item.game_data.iterate():
        if i.id not in values:
            yield "   0\t%s" % i


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u,--user", action="store_true", help="include user data", dest="user"
    )
    args = parser.parse_args()
    include_user: bool = args.user

    item_labels = _iter_item_labels(data.path("single_mode_item_labels.csv"))
    if include_user:
        item_labels = itertools.chain(
            item_labels, _iter_item_labels(config.single_mode_item_label_path)
        )
    for i in _item_stats(item_labels):
        print(i)


if __name__ == "__main__":
    main()
