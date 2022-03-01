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
from auto_derby.single_mode.item import Item, ItemEffect, g
import json
import pathlib


def _get_effects(db: sqlite3.Connection, group: int) -> Iterator[ItemEffect]:

    with contextlib.closing(
        db.execute(
            """
SELECT
  t1.id,
  t1.effect_group_id,
  t1.effect_type,
  t1.effect_value_1,
  t1.effect_value_2,
  t1.effect_value_3,
  t1.effect_value_4,
  t1.turn
  FROM single_mode_free_shop_effect AS t1
  WHERE t1.effect_group_id = ?
""",
            (group,),
        )
    ) as cur:
        for i in cur:
            assert len(i) == 8, i
            e = ItemEffect()
            (
                e.id,
                e.group,
                e.type,
                v1,
                v2,
                v3,
                v4,
                e.turn_count,
            ) = i
            e.values = (v1, v2, v3, v4)
            yield e


def _read_master_mdb(path: Text) -> Iterator[Item]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT
  t1.id,
  t2.text,
  t3.text,
  t1.coin_num,
  t1.limit_num,
  t1.effect_priority,
  t1.effect_group_id
  FROM single_mode_free_shop_item AS t1
  LEFT JOIN text_data AS t2 ON t2.category = 225 AND t2."index" = t1.item_id
  LEFT JOIN text_data AS t3 ON t3.category = 238 AND t3."index" = t1.item_id
;
    """
    )

    with contextlib.closing(cur):
        for i in cur:
            assert len(i) == 7, i
            v = Item()
            (
                v.id,
                v.name,
                v.description,
                v.original_price,
                v.max_quantity,
                v.effect_priority,
                effect_group,
            ) = i
            v.effects = tuple(_get_effects(db, effect_group))
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
