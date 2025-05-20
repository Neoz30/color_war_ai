from __future__ import annotations
from tic_tac_toe import Game, Shape
import random


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
        base = self.play_on.copy()
        points, move = self.search(base, self.shape)
        self.play_on.play(move, self.shape)

    def search(self, current: Game, shape: Shape) -> tuple:
        other = Shape.Cross
        if shape == Shape.Cross:
            other = Shape.Circle

        values = []
        for y in range(self.play_on.h):
            for x in range(self.play_on.w):
                if current.grid[y][x] != Shape.Empty:
                    continue

                think = current.copy()
                points, _ = think.play((x, y), shape)

                if think.end:
                    values.append((points, (x, y)))
                    continue

                values.append(self.search(think, other))

        choose_value = values[0]
        for value in values[1:]:
            if value[0] > choose_value[0]:
                choose_value = value

        choose_value = -choose_value[0], choose_value[1]
        return choose_value


game = Game()
human = Human(game, Shape.Cross)
players = [human, MiniMax(game, Shape.Circle)]

if random.randint(0, 1):
    players = players[1], players[0]

while not game.end:
    for player in players:
        player.get_info()
        player.play()

        if game.end:
            break

winner = game.verify()
if winner == Shape.Empty:
    print("Tie")
else:
    print(winner.name, "win !")
