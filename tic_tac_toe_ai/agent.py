import torch
import random
from collections import deque
from tic_tac_toe import Game, Shape
from model import Linear_QNet, QTrainer
import matplotlib.pyplot as plt

MAX_MEMORY = 800
BATCH_SIZE = 200
LR = 0.1


def argmax(tab: tuple | list) -> int:
    mi = 0
    for i in range(1, len(tab)):
        if tab[mi] < tab[i]:
            mi = i
    return mi


def random_move(state: tuple) -> list:
    moves = []
    for i in range(9):
        if state[i] == Shape.Empty:
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
        self.model = Linear_QNet(9,  9)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: Game) -> tuple:
        return tuple(shape.value for shape in game.grid)

    def remember(self, state: tuple, action: list, reward: int, next_state: tuple, done: bool):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) < BATCH_SIZE:
            mini_sample = random.sample(self.memory, len(self.memory))
        else:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
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

        if random.random() < self.epsilon or not max(prediction):
            return random_move(state)

        s = 0
        total = sum(prediction)
        r = random.random() * total
        for move, value in enumerate(prediction):
            if s <= r < s + value:
                final_move[move] = 1
                break
            s += value
        # final_move[torch.argmax(prediction)] = 1

        return final_move


def train():
    print("Init")
    agent = Agent()
    partner = Agent()
    agent.epsilon = 0

    epoch = 2500
    total_reward = 0
    hold_data = []
    all_reward = []

    shapes = (Shape.Cross, Shape.Circle)
    game = Game()
    players = agent, partner
    print("Start")

    done = False
    while True:
        for player, shape in zip(players, shapes):
            state_old = agent.get_state(game)
            final_move = agent.get_action(state_old)
            reward, done = game.play(argmax(final_move), shape)
            state_new = agent.get_state(game)

            hold_data.append([state_old, final_move, reward, state_new, done])

            if done:
                break

        if done:
            game.print_grid()

            s = Shape.Empty
            for player, shape in zip(players, shapes):
                if player is agent:
                    s = shape
                    break

            reward = game.win_score(s)
            for data in reversed(hold_data):
                data[2] += reward
                reward /= 2

                agent.train_short_memory(*data)
                agent.remember(*data)

                total_reward += data[2]
            hold_data.clear()

            game.reset()

            agent.n_games += 1
            agent.train_long_memory()
            # agent.epsilon = 0.5 - (agent.n_games / epoch)

            print('Game:', agent.n_games, 'Reward:', total_reward, 'Shape:', s.name)

            version = agent.n_games // (epoch // 20)
            partner.model.load(f"model_{random.randint(0, version)}.pth")

            if agent.n_games % (epoch // 20) == 1:
                agent.model.save(f"model_{version}.pth")

            if random.randint(0, 1):
                players = agent, partner
            else:
                players = partner, agent

            all_reward.append(total_reward)
            total_reward = 0

        if agent.n_games >= epoch:
            agent.model.save(f"model_final.pth")
            avg_sample = [sum(all_reward[i: i + 10]) / 10 for i in range(0, len(all_reward) - 1, 10)]

            plt.plot(all_reward, color="blue")
            plt.plot([i for i in range(0, len(all_reward) - 1, 10)], avg_sample, color="orange")
            plt.show()
            break


if __name__ == '__main__':
    train()
