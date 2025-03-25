import torch
from tic_tac_toe import Game, Shape
from agent import Agent
import random


def play_human() -> int:
    pos = "a", "b"
    while not (pos[0].isdigit() and pos[1].isdigit()):
        r = input("Where you play ? (position)")
        pos = r[0], r[3]

    pos = int(pos[0]), int(pos[1])
    return pos[0] + pos[1] * 3


def play_AI(agent: Agent, game: Game) -> int:
    moves = agent.get_action(
        agent.get_state(game)
    )
    mi = 0
    for i in range(1, len(moves)):
        if moves[mi] < moves[i]:
            mi = i
    return mi


game = Game()
shapes = (Shape.Cross, Shape.Circle)

ai = Agent()
ai.model.load_state_dict(torch.load("model/model_final.pth"))
human = None

players = [human, ai]
if random.randint(0, 1):
    players = players[1], players[0]

game_over = False
while True:
    for i_sh, shape in enumerate(shapes):
        player = players[i_sh]
        game.print_grid()

        if isinstance(player, Agent):
            game_over = game.play(play_AI(player, game), shape)[1]
        else:
            pos = play_human()
            while game.grid[pos] != Shape.Empty:
                pos = play_human()
            game_over = game.play(pos, shape)[1]

        if game_over:
            break

    if game_over:
        game.print_grid()
        winner = game.verify()
        if winner == Shape.Empty:
            print("Tie")
        else:
            print(winner.name, "win !")
        break
