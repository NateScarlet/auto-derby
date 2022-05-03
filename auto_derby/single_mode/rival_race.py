# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator, Protocol, Text

from .. import data, filetools
from .context import Context
from ..character import Character


class Repository(Protocol):
    def replace_data(self, it: Iterator[RivalRace], /) -> None:
        ...

    def find(
        self,
        *,
        name: Text = "",
        character_id: int = 0,
        character_name: Text = "",
        turn: int = 0,
    ) -> Iterator[RivalRace]:
        """
        find granted rival race (there are random rival races)

        >>> r = RivalRace.repository

        Get by name:
        >>> print(next(r.find(name="コスモス賞")))
        RivalRace<コスモス賞:タマモクロス#1021,ゴールドシチー#1040>

        Get by character and turn:
        >>> print(next(r.find(character_id=1001, turn=21)))
        RivalRace<京王杯ジュニアステークス:スペシャルウィーク#1001,グラスワンダー#1011>

        Iterate all:
        >>> for i in r.find():
        ...     pass
        """
        ...


class RivalRace:
    repository: Repository

    @classmethod
    def find(cls, ctx: Context) -> Iterator[RivalRace]:
        return cls.repository.find(
            character_id=ctx.character.id,
            turn=ctx.turn_count_v2(),
        )

    def __init__(
        self,
        turn: int,
        name: Text,
        character_ids: Iterable[int],
    ):
        self.turn = turn
        self.name = name
        self.character_ids = tuple(sorted(character_ids))
        self.character_names = tuple(
            next(Character.repository.find(id=i)).name for i in self.character_ids
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RivalRace):
            return False
        return (
            o.turn == self.turn
            and o.name == self.name
            and o.character_ids == self.character_ids
        )

    def __str__(self):
        character_text = ",".join(
            [
                f"{name}#{id_}"
                for name, id_ in zip(self.character_names, self.character_ids)
            ]
        )
        return f"RivalRace<{self.name}:{character_text}>"


class JSONLRepository(Repository):
    def __init__(self, path: Text) -> None:
        self.path = path

    def _to_po(self, c: RivalRace) -> Dict[Text, Any]:
        return {
            "turn": c.turn,
            "name": c.name,
            "characterNames": c.character_names,
            "characterIDs": c.character_ids,
        }

    def _from_po(self, data: Dict[Text, Any]) -> RivalRace:
        return RivalRace(
            data["turn"],
            data["name"],
            data["characterIDs"],
        )

    def replace_data(self, it: Iterator[RivalRace], /) -> None:
        with filetools.atomic_save_path(self.path) as save_path, open(
            save_path, "w", encoding="utf-8"
        ) as f:
            for i in it:
                json.dump(self._to_po(i), f, ensure_ascii=False)
                f.write("\n")

    def find(
        self,
        *,
        name: Text = "",
        character_id: int = 0,
        character_name: Text = "",
        turn: int = 0,
    ) -> Iterator[RivalRace]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    c = self._from_po(json.loads(line))
                    if name and c.name != name:
                        continue
                    if turn and c.turn != turn:
                        continue
                    if character_id and character_id not in c.character_ids:
                        continue
                    if character_name and character_name not in c.character_names:
                        continue
                    yield c
        except FileNotFoundError:
            return


RivalRace.repository = JSONLRepository(data.path("single_mode_rival_races.jsonl"))
