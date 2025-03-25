from __future__ import annotations
from enum import IntEnum


class Shape(IntEnum):
    Empty = 0
    Cross = 1
    Circle = 2


class Game:
    def __init__(self):
        self.grid = [Shape.Empty for _ in range(9)]
        self.row = 3

    def copy(self) -> Game:
        copied = Game()
        for i in range(9):
            copied.grid[i] = self.grid[i]
        return copied

    def print_grid(self):
        print()
        for i in range(9):
            print(('~', 'X', 'O')[self.grid[i]], end=" ")
            if i % self.row == 2:
                print()

    def reset(self):
        for i in range(9):
            self.grid[i] = Shape.Empty

    def full(self):
        return all([self.grid[i] != Shape.Empty for i in range(9)])

    def empty_move(self) -> list:
        empty = []
        for i in range(9):
            if self.grid[i] == Shape.Empty:
                empty.append(i)
        return empty

    def verify(self) -> Shape:
        for x in range(3):
            if self.grid[x] == self.grid[self.row + x] == self.grid[2 * self.row +x]:
                return self.grid[x]

        for y in range(3):
            if self.grid[y * self.row] == self.grid[y * self.row + 1] == self.grid[y * self.row + 2]:
                return self.grid[y * self.row]

        if self.grid[0] == self.grid[4] == self.grid[8]:
            return self.grid[0]
        if self.grid[2] == self.grid[4] == self.grid[6]:
            return self.grid[2]

        return Shape.Empty

    def win_score(self, shape: Shape) -> int:
        shape_win = self.verify()
        if shape_win == Shape.Empty:
            return 0
        if shape_win == shape:
            return 1
        else:
            return -1

    def play(self, action: int, shape: Shape) -> tuple:
        """
        :param action: La case en partant de en haut à gauche vers en bas à droite
        :param shape: La forme qui joue
        :return: récompense, fin de partie
        """

        game_over = False
        if self.grid[action] == Shape.Empty:
            self.grid[action] = shape

        winner = self.verify()
        if winner != Shape.Empty:
            game_over = True

        if self.full():
            game_over = True

        return 0, game_over
