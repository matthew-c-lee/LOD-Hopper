from enum import Enum, auto
from typing import NamedTuple, NewType
from dataclasses import dataclass


Blocks = NewType("Blocks", int)

class Coordinate(NamedTuple):
    x: Blocks
    z: Blocks


class Dimension(Enum):
    x = auto()
    y = auto()
    z = auto()

class Direction(Enum):
    positive = auto()
    negative = auto()

class SideInfo(Enum):
    east = ("north", "south", Direction.positive, Dimension.z)
    north = ("west", "east", Direction.negative, Dimension.x)
    west = ("south", "north", Direction.negative, Dimension.z)
    south = ("east", "west", Direction.positive, Dimension.x)

    @property
    def clockwise_moving(self):
        return self.value[0]

    @property
    def counter_clockwise_moving(self):
        return self.value[1]

    @property
    def direction(self):
        return self.value[2]

    @property
    def dimension_moving_in(self):
        return self.value[3]

class Side(NamedTuple):
    coordinates: tuple[Coordinate, ...]
    side_info: SideInfo


class TeleporationRing(NamedTuple):
    east: Side
    north: Side
    west: Side
    south: Side
