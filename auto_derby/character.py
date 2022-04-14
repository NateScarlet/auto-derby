# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import enum
import json
from typing import Any, Dict, Iterator, Protocol, Text, Tuple

from . import data, filetools


class Gender(enum.Enum):
    STALLION = 1
    MARE = 2


class Repository(Protocol):
    def replace_data(self, it: Iterator[Character], /) -> None:
        ...

    def find(self, *, name: Text = "", id: int = 0) -> Iterator[Character]:
        """
        >>> r = Character.repository

        Get by id:
        >>> print(next(r.find(id=1001)))
        Character<スペシャルウィーク#1001>

        Get by name:
        >>> print(next(r.find(name="スペシャルウィーク")))
        Character<スペシャルウィーク#1001>

        Iterate all:
        >>> for i in r.find():
        ...     pass
        """
        ...


class Character:
    UNKNOWN: Character

    repository: Repository

    def __init__(
        self,
        id: int,
        name: Text,
        real_name: Text,
        katakana: Text,
        voice: Text,
        birthday: Tuple[int, int, int],
        gender: Gender,
    ) -> None:
        self.id = id
        self.name = name
        self.real_name = real_name
        self.katakana = katakana
        self.voice = voice
        self.birthday = birthday
        self.gender = gender

    def __str__(self):
        return f"Character<{self.name}#{self.id}>"


Character.UNKNOWN = Character(0, "unknown", "?", "?", "?", (1970, 1, 1), Gender.MARE)


class JSONLRepository(Repository):
    def __init__(self, path: Text) -> None:
        self.path = path
        self._cache: Dict[int, Character] = {}

    def _to_po(self, c: Character) -> Dict[Text, Any]:
        return {
            "id": c.id,
            "name": c.name,
            "realName": c.real_name,
            "katakana": c.katakana,
            "voice": c.voice,
            "birthday": c.birthday,
            "gender": c.gender.name,
        }

    def _from_po(self, data: Dict[Text, Any]) -> Character:
        return Character(
            data["id"],
            data["name"],
            data["realName"],
            data["katakana"],
            data["voice"],
            tuple(data["birthday"]),
            Gender[data["gender"]],
        )

    def _iter(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    yield self._from_po(json.loads(line))
        except FileNotFoundError:
            return

    def replace_data(
        self,
        it: Iterator[Character],
    ) -> None:
        self._cache.clear()
        with filetools.atomic_save_path(self.path) as save_path, open(
            save_path, "w", encoding="utf-8"
        ) as f:
            for i in it:
                self._cache[i.id] = i
                json.dump(self._to_po(i), f, ensure_ascii=False)
                f.write("\n")

    def find(self, *, name: Text = "", id: int = 0) -> Iterator[Character]:
        if id in self._cache:
            yield self._cache[id]
            return
        try:
            if name:
                yield next(i for i in self._cache.values() if i.name == name)
                return
        except StopIteration:
            pass
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    c = self._from_po(json.loads(line))
                    self._cache[c.id] = c
                    if id and c.id != id:
                        continue
                    if name and c.name != name:
                        continue
                    yield c
                    if name or id:
                        return
        except FileNotFoundError:
            return


Character.repository = JSONLRepository(data.path("characters.jsonl"))
