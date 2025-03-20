import torch
import random
import math
from collections import deque
from tic_tac_toe import Game, Shape
from model import Linear_QNet, QTrainer
import matplotlib.pyplot as plt
from copy import deepcopy

MAX_MEMORY = 200
LR = 0.05

INF = math.inf


def argmax(tab: tuple | list) -> int:
    mi = 0
    for i in range(1, len(tab)):
        if tab[mi] < tab[i]:
            mi = i
    return mi


def random_move(game: Game) -> list:
    moves = []
    for i in range(9):
        if game.grid[i] == Shape.Empty:
            moves.append(i)
    final_move = [0 for _ in range(9)]
    final_move[random.choice(moves)] = 1
    return final_move


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(9, 36, 9)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: Game) -> tuple:
        return tuple(shape.value for shape in game.grid)

    def remember(self, state: tuple, action: list, reward: int, next_state: tuple, done: bool):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        random.shuffle(self.memory)
        mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state: tuple, action: list, reward: int, next_state: tuple, done: bool):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state: tuple) -> list:
        final_move = [0 for _ in range(9)]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)

        for imove, move in enumerate(prediction):
            if state0[imove] != 0:
                prediction[imove] = 0

        s = 0
        total = sum(prediction)
        r = random.random() * total
        for move, value in enumerate(prediction):
            if s <= r < s + value:
                final_move[move] = 1
                break
            s += value

        return final_move


def train():
    print("Init")
    shapes = (Shape.Cross, Shape.Circle)
    ag1, ag2 = Agent(), Agent()
    agents = (ag1, ag2)
    epoch = 400

    total_reward = [0, 0]
    game = Game()
    fill_at = 0

    all_reward1 = []
    all_reward2 = []
    print("Start")
    done = False
    while True:
        for i_shape, shape in enumerate(shapes):
            agent = agents[i_shape]

            state_old = agent.get_state(game)

            if agent is None or fill_at < MAX_MEMORY:
                final_move = random_move(game)

            else:
                final_move = agent.get_action(state_old)

            reward, done = game.play(argmax(final_move), shape)

            state_new = agent.get_state(game)
            agent.train_short_memory(state_old, final_move, reward, state_new, done)
            agent.remember(state_old, final_move, reward, state_new, done)

            total_reward[i_shape] += reward

            if done:
                fill_at += 1
                break

        if done:
            game.print_grid()
            game.reset()

            for i, agent in enumerate(agents):
                if fill_at >= MAX_MEMORY:
                    agent.n_games += 1
                agent.train_long_memory()

            print('Game', agents[0].n_games, 'Reward', total_reward)

            if ag1.n_games % 10 == 9:
                if total_reward[0] > total_reward[1]:
                    ag2 = deepcopy(ag1)
                else:
                    ag1 = deepcopy(ag2)

            if random.randint(0, 1):
                agents = ag2, ag1

            all_reward1.append(total_reward[0])
            all_reward2.append(total_reward[1])
            total_reward = [0, 0]

        if agents[0].n_games > epoch:
            ag1.model.save(f"model_ag1.pth")
            ag2.model.save(f"model_ag2.pth")

            plt.plot(all_reward1, color="red")
            plt.plot(all_reward2, color="blue")
            plt.show()
            break


if __name__ == '__main__':
    train()
