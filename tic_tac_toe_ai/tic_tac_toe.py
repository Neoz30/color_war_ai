from __future__ import annotations
from enum import IntEnum


class Shape(IntEnum):
    Empty = 0
    Cross = 1
    Circle = -1


class Game:
    def __init__(self):
        self.w = 3
        self.h = 3

        self.grid = [
            [
                Shape.Empty for _ in range(self.w)
            ] for _ in range(self.h)
        ]
        self.end = False

    def copy(self) -> Game:
        copied = Game()
        for y in range(self.h):
            for x in range(self.w):
                copied.grid[y][x] = self.grid[y][x]
        return copied

    def reset(self):
        for y in range(self.h):
            for x in range(self.w):
                self.grid[y][x] = Shape.Empty
        self.end = False

    def full(self):
        return all([self.grid[i // self.w][i % self.w] != Shape.Empty for i in range(self.w * self.h)])

    def verify(self) -> Shape:
        for x in range(self.w):
            if self.grid[0][x] == self.grid[1][x] == self.grid[2][x]:
                return self.grid[0][x]

        for y in range(self.w):
            if self.grid[y][0] == self.grid[y][1] == self.grid[y][2]:
                return self.grid[y][0]

        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return self.grid[0][0]
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            return self.grid[0][2]

        return Shape.Empty

    def play(self, position: tuple, shape: Shape) -> tuple:
        if self.grid[position[1]][position[0]] == Shape.Empty:
            self.grid[position[1]][position[0]] = shape

        reward = 0
        winner = self.verify()
        if winner != Shape.Empty or self.full():
            self.end = True

            if winner == shape:
                reward = 1
            else:
                reward = -1

        return reward, self.end
