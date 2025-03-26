from __future__ import annotations
from enum import IntEnum


class Shape(IntEnum):
    Empty = 0
    Cross = 1
    Circle = 2


class Game:
    def __init__(self):
        self.grid = [Shape.Empty for _ in range(9)]

    def copy(self) -> Game:
        copied = Game()
        for i in range(9):
            copied.grid[i] = self.grid[i]
        return copied

    def print_grid(self):
        print()
        for i in range(9):
            print(('~', 'X', 'O')[self.grid[i]], end=" ")
            if i % 3 == 2:
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
            if self.grid[x] == self.grid[3 + x] == self.grid[2 * 3 + x]:
                return self.grid[x]

        for y in range(3):
            if self.grid[y * 3] == self.grid[y * 3 + 1] == self.grid[y * 3 + 2]:
                return self.grid[y * 3]

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
    
    def stat_row(self, s: Shape, row: int) -> tuple:
        e, c, o = 0, 0, 0
        for x in range(3):
            current = self.grid[3 * row + x]
            if current == Shape.Empty:
                e += 1
            elif current == s:
                c += 1
            else:
                o += 1
        return e, c, o
    
    def stat_colum(self, s: Shape, colum: int) -> tuple:
        e, c, o = 0, 0, 0
        for y in range(3):
            current = self.grid[3 * y + colum]
            if current == Shape.Empty:
                e += 1
            elif current == s:
                c += 1
            else:
                o += 1
        return e, c, o
    
    def finish_line(self, s: Shape) -> int:
        total = 0

        for row in range(3):
            e, c, o = self.stat_row(s, row)
            if c < 2 and o < 2:
                continue

            if c > o:
                total += 1
            else:
                total -= 1

        for colum in range(3):
            e, c, o = self.stat_row(s, colum)
            if c < 2 and o < 2:
                continue

            if c > o:
                total += 1
            else:
                total -= 1

        e, c, o = 0, 0, 0
        for pos in (0, 4, 8):
            current = self.grid[pos]
            if current == Shape.Empty:
                e += 1
            elif current == s:
                c += 1
            else:
                o += 1
        if c >= 2 or o >= 2:
            if c > o:
                total += 1
            else:
                total -= 1

        e, c, o = 0, 0, 0
        for pos in (2, 4, 6):
            current = self.grid[pos]
            if current == Shape.Empty:
                e += 1
            elif current == s:
                c += 1
            else:
                o += 1
        if c >= 2 or o >= 2:
            if c > o:
                total += 1
            else:
                total -= 1

        return total

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

        return self.finish_line(shape), game_over
