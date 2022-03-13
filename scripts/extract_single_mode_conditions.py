# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words chara inout
""".  """


if True:
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Iterator, Text
import sqlite3
import argparse
import os
import contextlib
from auto_derby.single_mode.condition import g, Condition
import json
import pathlib


def _read_master_mdb(path: Text) -> Iterator[Condition]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT 
    t1."index",
    t1.text,
    t2.text
FROM text_data AS t1
LEFT JOIN text_data AS t2 WHERE t1.category = 142 AND t2.category = 143 AND t2."index" == t1."index"
;
    """
    )

    with contextlib.closing(cur):
        for i in cur:
            assert len(i) == 3, i
            v = Condition()
            (
                v.id,
                v.name,
                v.description,
            ) = i
            yield v


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default=os.path.expandvars(
            "${LocalAppData}Low/cygames/umamusume/master/master.mdb"
        ),
    )
    args = parser.parse_args()
    path: Text = args.path

    with pathlib.Path(g.data_path).open("w", encoding="utf-8") as f:
        for item in _read_master_mdb(path):
            json.dump(item.to_dict(), f, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
