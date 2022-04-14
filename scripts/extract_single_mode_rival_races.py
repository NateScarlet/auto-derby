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
from typing import Iterator, Sequence, Set, Text, Tuple

from auto_derby.single_mode import RivalRace


def _rival_race_characters(
    db: sqlite3.Connection,
    chara_id: int,
    turn: int,
    program_id: int,
) -> Set[int]:
    with contextlib.closing(
        db.execute(
            """
SELECT
  t1.chara_id,
  t1.rival_chara_id
  FROM single_mode_rival AS t1
  WHERE (t1.chara_id = ? OR t1.rival_chara_id = ?) AND t1.turn = ? AND t1.race_program_id = ?
;
""",
            (chara_id, chara_id, turn, program_id),
        )
    ) as cur:
        return set(j for i in cur.fetchall() for j in i)


def _read_master_mdb(path: Text) -> Iterator[RivalRace]:

    db = sqlite3.connect(path)
    cur = db.execute(
        """
SELECT
  t1.turn,
  COALESCE(t3.text, "") AS name,
  t1.chara_id,
  t1.race_program_id
  FROM single_mode_rival AS t1
  LEFT JOIN single_mode_program AS t2 ON t2.id = t1.race_program_id
  LEFT JOIN text_data AS t3 ON t3.category = 28 AND t3."index" = t2.race_instance_id
  ORDER BY t1.turn, t3.text
;
    """
    )

    with contextlib.closing(cur):
        seen: Set[Tuple[int, Text, Sequence[int]]] = set()
        for i in cur:
            turn, name, chara_id, program_id = i
            r = RivalRace(
                turn, name, _rival_race_characters(db, chara_id, turn, program_id)
            )
            key = (r.turn, r.name, tuple(r.character_ids))
            if key not in seen:
                yield r
                seen.add(key)


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

    RivalRace.repository.replace_data(_read_master_mdb(path))


if __name__ == "__main__":
    main()
