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

        #print(moves, f"Minimax think in {think_time} msec")

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

                if think.end or depth >= 4:
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

class Qlearning(Player):
    def __init__(self, game: Game, shape: int):
        super().__init__(game, shape)

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.vtable = {}

    def to1dgame(self, game: Game) -> tuple:
        return tuple(game.grid[i // game.size][i % game.size] for i in range(game.size**2))

    def evaluation(self, state) -> float:
        return self.vtable.get(state, 0)

    def update_vtable(self, state, reward, next_state):
        changes = self.alpha * (reward + self.gamma * self.vtable.get(next_state, 0) - self.vtable.get(state, 0))
        if state not in self.vtable:
            self.vtable[state] = changes
            return
        self.vtable[state] += changes

    def train(self):
        asigned_game = self.play_on
        asigned_shape = self.shape
        self.shape = Shape.Cross

        for episode in range(18000):
            print(episode)
            self.play_on = Game()
            opponent = MiniMax(self.play_on, Shape.Circle)

            if random.randint(0, 1):
                opponent.play()

            while not self.play_on.end:
                state = self.to1dgame(self.play_on)
                self.play_short()

                reward = 0
                if self.play_on.winner != Shape.Empty:
                    if self.play_on.winner == self.shape:
                        reward = 1
                    else:
                        reward = -1

                next_state = self.to1dgame(self.play_on)
                self.update_vtable(state, reward, next_state)

                if not self.play_on.end:
                    opponent.play()

        self.play_on = asigned_game
        self.shape = asigned_shape

    def play_short(self):
        s = self.play_on.size
        actions = [(i % s, i // s) for i in range(s**2) if self.play_on.grid[i // s][i % s] == Shape.Empty]

        if random.random() <= self.epsilon:
            self.play_on.play(random.choice(actions), self.shape)
            return

        best = actions[0]
        best_value = -math.inf
        for a in actions:
            think = self.play_on.copy()
            think.play(a, self.shape)
            v = self.vtable.get(self.to1dgame(think), 0.0)
            if v > best_value:
                best = a
                best_value = v
        self.play_on.play(best, self.shape)

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

        #print(moves, f"Qlearning think in {think_time} msec")

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

                if think.end or depth >= 4:
                    values[y][x] = self.evaluation(self.to1dgame(think))
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
qlearning = Qlearning(game, Shape.Circle)

qlearning.train()
with open("V-table.txt", 'x') as file:
    file.write(str(qlearning.vtable))

players = [human, qlearning]

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
