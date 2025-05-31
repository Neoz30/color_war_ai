from __future__ import annotations
from tic_tac_toe import Game, Shape
from time import time
import random
import math


class Player:
    def __init__(self, game: Game, shape: int):
        self.play_on = game
        self.shape = shape

    def get_info(self):
        pass

    def play(self):
        pass


class Human(Player):
    def get_info(self):
        for y in range(self.play_on.size):
            for x in range(self.play_on.size):
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
        start = time()
        moves = self.search(self.play_on, self.shape, 0)
        think_time = round(time() - start, 3) * 1000

        best_trust = -math.inf
        best_moves = []
        for y in range(self.play_on.size):
            for x in range(self.play_on.size):
                trust = moves[y][x]
                if trust > best_trust:
                    best_trust = trust
                    best_moves = [(x, y)]
                    continue

                if trust == best_trust:
                    best_moves.append((x, y))

        self.play_on.play(random.choice(best_moves), self.shape)

        print(moves, f"think in {think_time} msec")

    def search(self, current: Game, shape: int, depth: int) -> list[list[float]]:
        other = Shape.Cross
        if shape == Shape.Cross:
            other = Shape.Circle

        values: list[list[float]] = []
        for y in range(self.play_on.size):
            values.append([])
            for x in range(self.play_on.size):
                if shape == self.shape:
                    values[y].append(-math.inf)
                else:
                    values[y].append(math.inf)

                if current.grid[y][x] != Shape.Empty:
                    continue

                think = current.copy()
                think.play((x, y), shape)

                if think.end:
                    if think.winner == self.shape:
                        points = 1
                    elif think.winner == Shape.Empty:
                        points = 0
                    else:
                        points = -1

                    values[y][x] = points
                else:
                    moves = self.search(think, other, depth + 1)
                    if shape != self.shape:
                        value = max([max(l) for l in moves])
                    else:
                        value = min([min(l) for l in moves])
                    values[y][x] = value

        return values

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

match game.winner:
    case Shape.Empty:
        print("Tie")
    case Shape.Cross:
        print("Cross Win !")
    case Shape.Circle:
        print("Circle Win !")
