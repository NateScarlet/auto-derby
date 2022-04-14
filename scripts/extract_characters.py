# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words chara


if True:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import contextlib
import os
import sqlite3
from typing import Iterator, Text

from auto_derby.character import Character, Gender


def _read_master_mdb(path: Text) -> Iterator[Character]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT
  t1.id,
  t2.text,
  t3.text,
  t4.text,
  t5.text,
  t1.birth_year,
  t1.birth_month,
  t1.birth_day,
  t1.sex
  FROM chara_data AS t1
  LEFT JOIN text_data AS t2 ON t2.category = 6 AND t2."index" = t1.id
  LEFT JOIN text_data AS t3 ON t3.category = 170 AND t3."index" = t1.id
  LEFT JOIN text_data AS t4 ON t4.category = 182 AND t4."index" = t1.id
  LEFT JOIN text_data AS t5 ON t5.category = 7 AND t5."index" = t1.id
;
    """
    )

    with contextlib.closing(cur):
        for i in cur:
            yield Character(i[0], i[1], i[2], i[3], i[4], tuple(i[5:8]), Gender(i[8]))


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
    Character.repository.replace_data(_read_master_mdb(path))


if __name__ == "__main__":
    main()
