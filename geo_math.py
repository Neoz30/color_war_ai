from __future__ import annotations
from math import sqrt, cos, sin


class Vec2:
    """
    Math vector with 2 dimensions
    """

    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, position: tuple | list):
        self.x = position[0]
        self.y = position[1]

    def __getitem__(self, index: int):
        return self.pos[index]

    def __setitem__(self, index: int, value: int | float):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, c: int | float) -> Vec2:
        return Vec2(self.x * c, self.y * c)

    def __truediv__(self, c: int | float) -> Vec2:
        return Vec2(self.x / c, self.y / c)

    __radd__ = __add__
    __rmul__ = __mul__

    def lenght(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> Vec2:
        lenght = self.lenght()
        return self / lenght

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def det(self, other: Vec2) -> float:
        return self.x * other.y - self.y * other.x

    def rotate(self, angle: float) -> Vec2:
        sina, cosa = sin(angle), cos(angle)
        return Vec2(self.x * cosa - self.y * sina, self.x * sina + self.y * cosa)
