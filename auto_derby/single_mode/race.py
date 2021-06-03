# -*- coding=UTF-8 -*-
# pyright: strict
""".  """


from typing import Dict, Text, Tuple, Any


class Race:

    GROUND_GRASS = 1
    GROUND_DART = 2

    TRACK_IN = 1
    TRACK_MIDDLE = 2
    TRACK_OUT = 3

    TARGET_STATUS_SPEED = 1
    TARGET_STATUS_STAMINA = 2
    TARGET_STATUS_POWER = 3
    TARGET_STATUS_PERSERVANCE = 4
    TARGET_STATUS_INTELLIGENCE = 5

    PERMISSION_JUNIOR = 1
    PERMISSION_CLASSIC = 2
    PERMISSION_JUNIOR_OR_CLASSIC = 3
    PERMISSION_SENIOR = 4
    PERMISSION_URA = 5

    GRADE_DEBUT = 900
    GRADE_NOT_WINNING = 800
    GRADE_PRE_OP = 700
    GRADE_OP = 400
    GRADE_G3 = 300
    GRADE_G2 = 200
    GRADE_G1 = 100

    TURN_LEFT = 1
    TURN_RIGHT = 2
    TURN_NONE = 4

    def __init__(self):
        self.name: Text = ''
        self.permission: int = 0
        self.month: int = 0
        self.half: int = 0
        self.grade: int = 0
        self.entry_count: int = 0
        self.distance: int = 0
        self.min_fan_count: int = 0

        self.ground: int = 0
        self.track: int = 0
        self.turn: int = 0
        self.target_statuses: Tuple[int, ...] = ()

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "name": self.name,
            "permission": self.permission,
            "month": self.month,
            "half": self.half,
            "grade": self.grade,
            "entryCount": self.entry_count,
            "distance": self.distance,
            "ground": self.ground,
            "track": self.track,
            "turn": self.turn,
            "targetStatuses": self.target_statuses,
            "minFanCount": self.min_fan_count
        }
