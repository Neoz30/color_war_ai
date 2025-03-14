from enum import IntEnum


class Shape(IntEnum):
    Empty = 0
    Cross = 1
    Circle = 2


class Game:
    def __init__(self):
        self.grid = [[Shape.Empty for _ in range(3)] for _ in range(3)]

    def print_grid(self):
        print()
        for y in range(3):
            for x in range(3):
                print(('~', 'X', 'O')[self.grid[y][x]], end=" ")
            print()

    def reset(self):
        for y in range(3):
            for x in range(3):
                self.grid[y][x] = Shape.Empty

    def full(self):
        return all([self.grid[i // 3][i % 3] != 0 for i in range(9)])

    def verify(self) -> Shape:
        for x in range(3):
            if self.grid[0][x] == self.grid[1][x] == self.grid[2][x]:
                return self.grid[0][x]

        for y in range(3):
            if self.grid[y][0] == self.grid[y][1] == self.grid[y][2]:
                return self.grid[y][0]

        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return self.grid[0][0]
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            return self.grid[0][2]

        return Shape.Empty

    def play(self, action: int, shape: Shape) -> tuple:
        """
        :param action: La case en partant de en haut à gauche vers en bas à droite
        :param shape: La forme qui joue
        :return: récompense, fin de partie
        """
        reward, game_over = 0, False

        x = action % 3
        y = action // 3
        if self.grid[y][x] == Shape.Empty:
            self.grid[y][x] = shape

        v = self.verify()
        if v == shape:
            reward += 1
            game_over = True
        elif v != Shape.Empty:
            reward -= 1
            game_over = True

        if self.full():
            game_over = True
        return reward, game_over

