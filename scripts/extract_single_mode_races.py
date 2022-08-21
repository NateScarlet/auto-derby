# -*- coding=UTF-8 -*-
# pyright: strict
# spell-checker: words chara inout
""".  """


if True:
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Any, Dict, Iterator, Set, Text, Tuple
import sqlite3
import argparse
import os
import contextlib
from auto_derby.single_mode.race import Race


from auto_derby.single_mode.race.race import Course

_ID_NAMESPACE = (
    (
        # manually increase this before add new entry in middle
        1
    )
    .to_bytes(2, "big")
    .hex()
)


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


def _race_grade_points(db: sqlite3.Connection, group: int, grade: int) -> Tuple[int]:
    d: Dict[int, int] = {}

    with contextlib.closing(
        db.execute(
            """
SELECT 
  t1.order_min,
  t1.order_max,
  t1.point_num
  FROM single_mode_free_win_point as t1
  WHERE race_group_id = ? AND grade = ?
;
""",
            (group, 0 if group else grade),
        )
    ) as cur:
        for start, end, value in cur:
            for order in range(start, end + 1):
                d[order] = value

    if not d:
        return _race_grade_points(db, 0, grade)

    return tuple(v for _, v in sorted(d.items()))


def _race_shop_coins(db: sqlite3.Connection, grade: int) -> Tuple[int]:
    d: Dict[int, int] = {}

    with contextlib.closing(
        db.execute(
            """
SELECT 
  t1.order_min,
  t1.order_max,
  t1.coin_num
  FROM single_mode_free_coin_race as t1
  WHERE grade = ?
;
""",
            (grade,),
        )
    ) as cur:
        for start, end, value in cur:
            for order in range(start, end + 1):
                d[order] = value

    return tuple(v for _, v in sorted(d.items()))


def _race_courses(db: sqlite3.Connection, course_set: int) -> Iterator[Course]:

    with contextlib.closing(
        db.execute(
            """
SELECT 
  t1.distance,
  t1.ground,
  t1.inout,
  t1.turn,
  t2.text AS stadium,
  t3.target_status_1,
  t3.target_status_2
  FROM race_course_set as t1
  LEFT JOIN text_data AS t2 ON t2.category = 35 AND t2."index" = t1.race_track_id
  LEFT JOIN race_course_set_status AS t3 ON t3.course_set_status_id = t1.course_set_status_id
  WHERE t1.id = ?
;
""",
            (course_set,),
        )
    ) as cur:
        for (
            distance,
            ground,
            inout,
            turn,
            stadium,
            target_status_1,
            target_status_2,
        ) in cur:
            yield Course(
                stadium=stadium,
                ground=ground,
                distance=distance,
                track=inout,
                turn=turn,
                target_statuses=tuple(
                    i for i in (target_status_1, target_status_2) if i
                ),
            )


def _read_master_mdb(path: Text) -> Iterator[Race]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT
  t4.text,
  t1.month,
  t1.half,
  t3.grade,
  t1.race_permission,
  t1.need_fan_count,
  t1.fan_set_id,
  t3.entry_num,
  t3.course_set,
  t1.program_group,
  COALESCE(t8.race_group_id, 0)
  FROM single_mode_program AS t1
  LEFT JOIN race_instance AS t2 ON t1.race_instance_id = t2.id
  LEFT JOIN race AS t3 ON t2.race_id = t3.id
  LEFT JOIN text_data AS t4 ON t4.category = 28 AND t2.id = t4."index"
  LEFT JOIN single_mode_race_group AS t8 ON t8.race_program_id = t1.program_group
  ORDER BY t1.race_permission, t1.month, t1.half, t3.grade, t1.id DESC
;
    """
    )

    with contextlib.closing(cur):
        for i in cur:
            v = Race()
            (
                v.name,
                v.month,
                v.half,
                v.grade,
                v.permission,
                v.min_fan_count,
                fan_set_id,
                v.entry_count,
                course_set_id,
                program_group,
                race_group,
            ) = i
            v.courses = tuple(_race_courses(db, course_set_id))
            v.fan_counts = _get_fan_set(db, fan_set_id)
            if program_group:
                v.characters = _program_group_characters(db, program_group)
            v.grade_points = _race_grade_points(db, race_group, v.grade)
            v.shop_coins = _race_shop_coins(db, v.grade)
            yield v


def _merge_races(ordered_input: Iterator[Race]) -> Iterator[Race]:
    def _dict_key(do: Race):
        return (
            do.name,
            do.min_fan_count,
            do.fan_counts,
            tuple(sorted(do.characters)),
            do.shop_coins,
            do.grade_points,
            do.entry_count,
        )

    m: Dict[Any, Race] = {}

    def _flush():
        yield from sorted(m.values(), key=lambda x: x.name)
        m.clear()

    def _group_key(do: Race):
        return (do.permission, do.month, do.half, do.grade)

    next_id = 1

    last_group_key = _group_key(Race())
    for i in ordered_input:
        gk = _group_key(i)
        if gk != last_group_key:
            yield from _flush()
            last_group_key = gk
        dk = _dict_key(i)
        if dk in m:
            match = m[dk]
            match.courses = tuple(
                (*match.courses, *(i for i in i.courses if i not in match.courses))
            )
        else:
            i.id = f"{_ID_NAMESPACE}-{next_id.to_bytes(2, 'big').hex()}"
            next_id += 1
            m[dk] = i

    yield from _flush()


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

    Race.repository.replace_data(_merge_races(_read_master_mdb(path)))


if __name__ == "__main__":
    main()
