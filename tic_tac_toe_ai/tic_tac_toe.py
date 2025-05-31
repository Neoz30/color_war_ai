from __future__ import annotations


class Shape:
    Empty = 0
    Cross = 1
    Circle = -1


class Game:
    def __init__(self):
        self.size = 3

        self.grid = [
            [
                Shape.Empty for _ in range(self.size)
            ] for _ in range(self.size)
        ]

        self.winner = Shape.Empty
        self.end = False

    def copy(self) -> Game:
        copied = Game()
        for y in range(self.size):
            for x in range(self.size):
                copied.grid[y][x] = self.grid[y][x]
        return copied

    def reset(self):
        for y in range(self.size):
            for x in range(self.size):
                self.grid[y][x] = Shape.Empty
        self.end = False

    def full(self):
        return all([self.grid[i // self.size][i % self.size] != Shape.Empty for i in range(self.size * self.size)])

    def verify_at(self, position: tuple) -> int:
        cx, cy = position
        current = self.grid[cy][cx]

        if all(self.grid[cy][x] == current for x in range(self.size)):
            return current

        if all(self.grid[y][cx] == current for y in range(self.size)):
            return current

        if cx == cy and all(current == self.grid[d][d] for d in range(self.size)):
            return current

        last = self.size - 1
        if cx + cy == last and all(current == self.grid[d][last - d] for d in range(self.size)):
            return current

        return Shape.Empty

    def play(self, position: tuple, shape: int):
        x, y = position
        if self.grid[y][x] == Shape.Empty:
            self.grid[y][x] = shape

        self.winner = self.verify_at(position)
        if self.full() or self.winner != Shape.Empty:
            self.end = True
