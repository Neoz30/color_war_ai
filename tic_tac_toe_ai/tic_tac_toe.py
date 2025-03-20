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
        return all([self.grid[i] != 0 for i in range(9)])

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

    def missing1_opponent(self, shape: Shape) -> bool:
        # Not fully working
        for x in range(3):
            c = 0
            for offset in range(3):
                value = self.grid[offset * self.row + x]
                if value == shape:
                    c = 0
                    break
                elif value != Shape.Empty:
                    c += 1
            if c >= 2:
                return True

        for y in range(3):
            c = 0
            for offset in range(3):
                value = self.grid[y * self.row + offset]
                if value == shape:
                    c = 0
                    break
                elif value != Shape.Empty:
                    c += 1
            if c >= 2:
                return True

        c = 0
        for offset in range(0, 9, 4):
            value = self.grid[offset]
            if value == shape:
                c = 0
                break
            elif value != Shape.Empty:
                c += 1
        if c >= 2:
            return True

        c = 0
        for offset in range(2, 7, 2):
            value = self.grid[offset]
            if value == shape:
                c = 0
                break
            elif value != Shape.Empty:
                c += 1
        if c >= 2:
            return True

        return False

    def win(self, shape: Shape):
        return self.verify() == shape

    def play(self, action: int, shape: Shape) -> tuple:
        """
        :param action: La case en partant de en haut à gauche vers en bas à droite
        :param shape: La forme qui joue
        :return: récompense, fin de partie
        """

        game_over = False
        if self.grid[action] == Shape.Empty:
            self.grid[action] = shape

        win = self.win(shape)
        score = 0
        if self.missing1_opponent(shape):
            score = -1
        if win:
            score = 1
            game_over = True

        if self.full():
            game_over = True

        return score, game_over
