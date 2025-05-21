from __future__ import annotations
from tic_tac_toe import Game, Shape
import random
import math


class Player:
    def __init__(self, game: Game, shape: Shape):
        self.play_on = game
        self.shape = shape

    def get_info(self):
        pass

    def play(self):
        pass


class Human(Player):
    def get_info(self):
        for y in range(self.play_on.h):
            for x in range(self.play_on.w):
                shape = self.play_on.grid[y][x]
                show = '~'
                if shape == Shape.Cross:
                    show = 'X'
                if shape == Shape.Circle:
                    show = 'O'
                print(show, end=' ')
            print()

    def play(self):
        x, y = '#', '#'
        while not x.isdigit() or not y.isdigit():
            text = input("Where you play ? (x, y)")
            part = text.split()
            if len(part) != 2:
                continue
            x, y = part

        x, y = int(x), int(y)
        self.play_on.play((x, y), self.shape)


class MiniMax(Player):
    def play(self):
        other = Shape.Cross
        if self.shape == Shape.Cross:
            other = Shape.Circle

        values: list[list[int | None]] = []
        for y in range(self.play_on.h):
            values.append([])
            for x in range(self.play_on.w):
                values[y].append(None)

                if self.play_on.grid[y][x] != Shape.Empty:
                    continue

                think = self.play_on.copy()
                points, _ = think.play((x, y), self.shape)

                if think.end:
                    values[y][x] = points
                    continue

                values[y][x] = -self.search(think, other, 1)

        print(values)

        best_value = -math.inf
        best_move = None
        for y in range(self.play_on.h):
            for x in range(self.play_on.w):
                value = values[y][x]
                if value is None:
                    continue
                if value == best_value and random.randint(0, 1):
                    best_value = value
                    best_move = (x, y)
                elif value > best_value:
                    best_value = value
                    best_move = (x, y)

        self.play_on.play(best_move, self.shape)

    def search(self, current: Game, shape: Shape, depth: int) -> float:
        other = Shape.Cross
        if shape == Shape.Cross:
            other = Shape.Circle

        values: list[list[int | None]] = []
        for y in range(self.play_on.h):
            values.append([])
            for x in range(self.play_on.w):
                values[y].append(None)

                if current.grid[y][x] != Shape.Empty:
                    continue

                think = current.copy()
                points, _ = think.play((x, y), shape)

                if think.end:
                    values[y][x] = points
                    continue

                values[y][x] = -self.search(think, other, depth + 1)

        if depth == 0: print(values)

        choose_value = -math.inf
        for row in values:
            for value in row:
                if value is None:
                    continue
                if value > choose_value:
                    choose_value = value

        return choose_value

for party in range(10):
    game = Game()
    human = Human(game, Shape.Cross)
    players = [MiniMax(game, Shape.Cross), MiniMax(game, Shape.Circle)]

    if random.randint(0, 1):
        players = players[1], players[0]

    while not game.end:
        for player in players:
            player.get_info()
            player.play()
            human.get_info()

            if game.end:
                break

    winner = game.verify()
    if winner == Shape.Empty:
        print("Tie")
    else:
        print(winner.name, "win !")
