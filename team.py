from enum import Flag, auto


class Team(Flag):
    Red = auto()
    Blue = auto()
    Green = auto()
    Yellow = auto()
    Neutral = auto()
    playable = Red | Blue | Green | Yellow
