from __future__ import annotations

import math

from ai import *

import pyxel

FPS = 60
WINDOW_SIZE = (128, 128)

pyxel.init(WINDOW_SIZE[0], WINDOW_SIZE[1], display_scale=4, fps=FPS)

pyxel.load("ressources.pyxres")
# pyxel.playm(0, loop=True)

pyxel.mouse(False)

TEX_RES = (16, 16)
TEAM_COLOR = ((240, 240), (0, 0), (16, 0), (32, 0), (48, 0))


class Tile:
    def __init__(self, team: int = 0, charge: int = 0):
        self.team = team
        self.charge = charge

    def copy(self):
        return Tile(self.team, self.charge)

    def pick(self, other: Tile):
        self.team = other.team
        self.charge = other.charge

    def draw(self, pos: tuple):
        if self.team == 0:
            return

        pyxel.blt(
            pos[0], pos[1], 0,
            TEAM_COLOR[self.team][0], TEAM_COLOR[self.team][1],
            TEX_RES[0], TEX_RES[1],
            0
        )
        color = 9 if self.charge > 4 else 13
        pyxel.text(pos[0] + 6, pos[1] + 6, str(min(self.charge, 4)), color)
        pyxel.text(pos[0] + 6, pos[1] + 5, str(min(self.charge, 4)), 7)

    def animation(self, interpolate: float, start: tuple, final: tuple):
        pos = (
            start[0] * (1 - interpolate) + final[0] * interpolate,
            start[1] * (1 - interpolate) + final[1] * interpolate,
        )

        self.draw(pos)


class Board:
    def __init__(self, size: tuple):
        self.size = size
        self._board = [
            [Tile() for _ in range(size[1])] for _ in range(size[0])
        ]
        self.buffer = [
            [Tile() for _ in range(size[1])] for _ in range(size[0])
        ]

        # Graphic attribute
        self.offset = (
            (pyxel.width - size[0] * TEX_RES[0]) // 2,
            (pyxel.height - size[1] * TEX_RES[1]) // 2
        )

    def __getitem__(self, item: tuple):
        return self._board[item[0]][item[1]]

    def __setitem__(self, key: tuple, value: Tile):
        self._board[key[0]][key[1]] = value

    def pos_to_screen(self, pos: tuple) -> tuple:
        return pos[0] * TEX_RES[0] + self.offset[0], pos[1] * TEX_RES[1] + self.offset[1]

    def draw_back(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                graphic_pos = self.pos_to_screen((x, y))
                pyxel.blt(graphic_pos[0], graphic_pos[1], 0, 0, 32, TEX_RES[0], TEX_RES[1])

    def draw(self, anim_step: float, anim_time: float = 0.25) -> float:
        self.draw_back()
        interpolate = math.sqrt(anim_step / anim_time)
        four = False

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                graphic_pos = self.pos_to_screen((x, y))
                if self[x, y].charge > 3:
                    four = True
                    clone = self[x, y].copy()
                    clone.charge -= 3

                    if y + 1 < self.size[1]:
                        up = self.pos_to_screen((x, y + 1))
                        clone.animation(interpolate, graphic_pos, up)
                    if x + 1 < self.size[0]:
                        right = self.pos_to_screen((x + 1, y))
                        clone.animation(interpolate, graphic_pos, right)
                    if y > 0:
                        down = self.pos_to_screen((x, y - 1))
                        clone.animation(interpolate, graphic_pos, down)
                    if x > 0:
                        left = self.pos_to_screen((x - 1, y))
                        clone.animation(interpolate, graphic_pos, left)
                else:
                    self[x, y].draw(graphic_pos)

        if four and anim_step < anim_time:
            return anim_step + round(1 / FPS, 3)
        else:
            return 0

    def update(self, tile_pos: tuple):
        if self[tile_pos].charge < 4:
            return

        inc = self[tile_pos].charge - 3  # Add the bomb chain bug
        for offset in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            side_tile = (tile_pos[0] + offset[0], tile_pos[1] + offset[1])
            if not (0 <= side_tile[0] < self.size[0] and 0 <= side_tile[1] < self.size[1]):
                continue

            self.buffer[side_tile[0]][side_tile[1]].charge += inc
            self.buffer[side_tile[0]][side_tile[1]].team = self[tile_pos].team

        # Clear current tile
        self.buffer[tile_pos[0]][tile_pos[1]].team = 0
        self.buffer[tile_pos[0]][tile_pos[1]].charge = 0

    def turn(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.update((x, y))
        # Copy buffer to board
        need = False
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self[x, y].pick(self.buffer[x][y])
                if self[x, y].charge < 4: continue
                need = True
        return need

    def alive_team(self) -> list:
        alive = []
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if not self[x, y].team or self[x, y].team in alive:
                    continue
                alive.append(self[x, y].team)
        return sorted(alive)


# Graphic function
def draw_mouse(team):
    pyxel.blt(pyxel.mouse_x, pyxel.mouse_y, 0, TEX_RES[0] * (team - 1), 16, TEX_RES[0], TEX_RES[1], 0)


def team_winner(team: int):
    team_color = [14, 6, 11, 10]
    match team:
        case 1:
            team_name = "Red"
        case 2:
            team_name = "Blue"
        case 3:
            team_name = "Green"
        case 4:
            team_name = "Yellow"
        case _:
            team_name = "Void"
    show = team_name + " win !"

    of_x = len(show) * 4 // 2
    of_y = 2

    pyxel.text(WINDOW_SIZE[0]//2 - of_x, 5 - of_y, show, team_color[team-1])
    pyxel.text(WINDOW_SIZE[0]//2 - of_x, 4 - of_y, show, 7)


def tie_end():
    pyxel.text(54, 63, "Tie !", 13)
    pyxel.text(54, 62, "Tie !", 7)


board = Board((7, 7))

# Initial team position
for i in range(4):
    x = board.size[0] - 2 if i & 1 else 1
    y = board.size[1] - 2 if i & 2 else 1
    board.buffer[x][y].team = i+1
    board.buffer[x][y].charge = 3
board.turn()

need = False

alive_team = [1, 2, 3, 4]
remain = [1, 2, 3, 4]

while True:
    for team_playing in alive_team:
        # Check if it can play
        if team_playing not in remain:
            continue

        # Get player input
        while True:
            # Maintien the window
            pyxel.cls(0)
            board.draw(0)
            draw_mouse(team_playing)
            pyxel.flip()

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                tile_pos = (
                    (pyxel.mouse_x - board.offset[0]) // TEX_RES[0],
                    (pyxel.mouse_y - board.offset[1]) // TEX_RES[1]
                )
                if 0 <= tile_pos[0] < board.size[0] and 0 <= tile_pos[1] < board.size[1]:
                    if board[tile_pos].team == team_playing:
                        click_pos = tile_pos
                        break

        board.buffer[tile_pos[0]][tile_pos[1]].charge += 1

        # Board update
        while True:
            pyxel.cls(0)
            anim_step = board.draw(0)
            draw_mouse(team_playing)
            pyxel.flip()
            while anim_step > 0:
                pyxel.cls(0)
                anim_step = board.draw(anim_step)
                draw_mouse(team_playing)
                pyxel.flip()

            end = not board.turn()
            remain = board.alive_team()
            if end or len(remain) < 2:
                break

    alive_team = board.alive_team()
    # Stop if 1 team or 0 remain
    if len(alive_team) < 2:
        who_won = None if len(alive_team) == 0 else alive_team[0]
        break

# End loop
while True:
    pyxel.cls(0)
    board.draw(0)
    if who_won is None:
        tie_end()
    else:
        team_winner(who_won)
    pyxel.flip()
