# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Any, Dict, Text, Tuple


class Effect:
    TYPE_PROPERTY = 1
    TYPE_TRAINING_LEVEL = 2
    TYPE_FRIENDSHIP = 3
    TYPE_CONDITION = 6
    TYPE_TRAINING_PARTNER_REASSIGN = 10
    TYPE_TRAINING_BUFF = 11
    TYPE_TRAINING_VITALITY_DEBUFF = 12
    TYPE_TRAINING_NO_FAILURE = 13
    TYPE_RACE_BUFF = 14

    PROPERTY_SPEED = 1
    PROPERTY_STAMINA = 2
    PROPERTY_POWER = 3
    PROPERTY_GUTS = 4
    PROPERTY_WISDOM = 5
    PROPERTY_VITALITY = 10
    PROPERTY_MAX_VITALITY = 11
    PROPERTY_MOOD = 20

    TRAINING_LEVEL_SPEED = 101
    TRAINING_LEVEL_STAMINA = 105
    TRAINING_LEVEL_POWER = 102
    TRAINING_LEVEL_GUTS = 103
    TRAINING_LEVEL_WISDOM = 106

    CONDITION_ADD = 1
    CONDITION_REMOVE = 2

    RACE_BUFF_REWARD = 6
    RACE_BUFF_FAN = 40

    FRIENDSHIP_SUPPORT = 1
    FRIENDSHIP_CHARACTER = 2

    def __init__(self) -> None:
        self.id = 0
        self.group = 0
        self.type = 0
        self.values: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self.turn_count = 0

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "id": self.id,
            "group": self.group,
            "type": self.type,
            "values": self.values,
            "turnCount": self.turn_count,
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> Effect:
        v = cls()
        v.id = d["id"]
        v.group = d["group"]
        v.type = d["type"]
        v.values = tuple(d["values"])
        v.turn_count = d["turnCount"]

        return v
