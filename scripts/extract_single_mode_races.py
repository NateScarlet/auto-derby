# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words chara inout
""".  """


if True:
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Iterator, Set, Text, Tuple
import sqlite3
import argparse
import os
import contextlib
from auto_derby.single_mode.race import Race, g
import json
import pathlib


def _get_fan_set(db: sqlite3.Connection, fan_set_id: int) -> Tuple[int, ...]:

    with contextlib.closing(
        db.execute(
            """
SELECT fan_count
  FROM single_mode_fan_count
  WHERE fan_set_id = ?
  ORDER BY "order"
;
""",
            (fan_set_id,),
        )
    ) as cur:
        return tuple(i[0] for i in cur.fetchall())


def _program_group_characters(db: sqlite3.Connection, program_group: int) -> Set[Text]:
    with contextlib.closing(
        db.execute(
            """
SELECT t2.text
  FROM single_mode_chara_program as t1
  LEFT JOIN text_data AS t2 ON t2.category = 182 AND t1.chara_id = t2."index"
  WHERE program_group = ?
  ORDER BY t2.text
;
""",
            (program_group,),
        )
    ) as cur:
        return set(i[0] for i in cur.fetchall())


def _read_master_mdb(path: Text) -> Iterator[Race]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT
  t4.text,
  t7.text AS stadium,
  t1.month,
  t1.half,
  t3.grade,
  t1.race_permission,
  t1.need_fan_count,
  t1.fan_set_id,
  t3.entry_num,
  t5.distance,
  t5.ground,
  t5.inout,
  t5.turn,
  t1.program_group,
  t6.target_status_1,
  t6.target_status_2
  FROM single_mode_program AS t1
  LEFT JOIN race_instance AS t2 ON t1.race_instance_id = t2.id
  LEFT JOIN race AS t3 ON t2.race_id = t3.id
  LEFT JOIN text_data AS t4 ON t4.category = 28 AND t2.id = t4."index"
  LEFT JOIN race_course_set AS t5 ON t5.id = t3.course_set
  LEFT JOIN race_course_set_status AS t6 ON t6.course_set_status_id = t5.course_set_status_id
  LEFT JOIN text_data AS t7 ON t7.category = 35 AND t7."index" = t5.race_track_id
  ORDER BY t1.race_permission, t1.month, t1.half, t3.grade DESC
;
    """
    )

    with contextlib.closing(cur):
        for i in cur:
            assert len(i) == 16, i
            v = Race()
            (
                v.name,
                v.stadium,
                v.month,
                v.half,
                v.grade,
                v.permission,
                v.min_fan_count,
                fan_set_id,
                v.entry_count,
                v.distance,
                v.ground,
                v.track,
                v.turn,
                program_group,
            ) = i[:-2]
            v.target_statuses = tuple(j for j in i[-2:] if j)
            v.fan_counts = _get_fan_set(db, fan_set_id)
            if program_group:
                v.characters = _program_group_characters(db, program_group)
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
        for race in _read_master_mdb(path):
            json.dump(race.to_dict(), f, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
