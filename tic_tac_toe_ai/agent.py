import torch
import random
import numpy as np
import math
from collections import deque
from tic_tac_toe import Game, Shape
from model import Linear_QNet, QTrainer

MAX_MEMORY = 1000
BATCH_SIZE = 100
LR = 0.1

INF = math.inf


def random_move(game: Game):
    moves = []
    for x in range(3):
        for y in range(3):
            if game.grid[y][x] == Shape.Empty:
                moves.append(3 * y + x)
    return random.choice(moves)


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(9, 36, 9)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        state = np.zeros(9, int)
        for i in range(9):
            s = game.grid[i // 3][i % 3]
            match s:
                case Shape.Cross:
                    state[i] = 1
                case Shape.Circle:
                    state[i] = -1
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 1000 - self.n_games
        final_move = [0 for _ in range(9)]
        if random.randint(0, 100) < self.epsilon:
            moves = []
            for v in range(9):
                if state[v] == 0:
                    moves.append(v)
            final_move[random.choice(moves)] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            for imove, move in enumerate(prediction):
                if state0[imove] != 0:
                    prediction[imove] = 0

            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    print("Init")
    shapes = (Shape.Cross, Shape.Circle)
    agents = (Agent(), Agent())
    total_reward = [0, 0]
    best_reward = [0, 0]
    game = Game()
    print("Start")

    done = False
    while True:
        for i_shape, shape in enumerate(shapes):
            agent = agents[i_shape]
            # game.print_grid()

            if agent is None:
                game.play(random_move(game), shape)
                continue

            # get old state
            state_old = agent.get_state(game)

            # get move
            final_move = agent.get_action(state_old)

            # perform move and get new state
            mi = 0
            for i in range(1, len(final_move)):
                if final_move[mi] < final_move[i]:
                    mi = i
            reward, done = game.play(mi, shape)
            state_new = agent.get_state(game)

            # train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            agent.remember(state_old, final_move, reward, state_new, done)

            total_reward[i_shape] += reward

            if done:
                break

        if done:
            game.print_grid()
            game.reset()

            for i, agent in enumerate(agents):
                agent.n_games += 1
                agent.train_long_memory()

                if total_reward[i] > best_reward[i]:
                    best_reward[i] = total_reward[i]
                    agent.model.save(f"model{i}.pth")

            print('Game', agents[0].n_games, 'Reward', total_reward, 'Best:', best_reward)
            total_reward = [0, 0]

        if agents[0].n_games > 2000:
            break


if __name__ == '__main__':
    train()
