from __future__ import annotations
from random import shuffle
from player import *
from team import Team
import pyxel


class Tile:
    def __init__(self, team: Team = Team.Neutral, charge: int = 0):
        self.team = team
        self.charge = charge

    def copy(self) -> Tile:
        return Tile(self.team, self.charge)

    def pick(self, other: Tile):
        self.team = other.team
        self.charge = other.charge


class Board:
    def __init__(self, width: int, lenght: int):
        self.width, self.lenght = width, lenght

        self.front = [
            [Tile() for _ in range(lenght)] for _ in range(width)
        ]
        self.back = [
            [Tile() for _ in range(lenght)] for _ in range(width)
        ]

    def explode_tile(self, x: int, y: int):
        tile = self.front[x][y]
        power = tile.charge - 3

        if x > 0:
            self.back[x - 1][y].team = tile.team
            self.back[x - 1][y].charge += power
        if y > 0:
            self.back[x][y - 1].team = tile.team
            self.back[x][y - 1].charge += power
        if x + 1 < self.width:
            self.back[x + 1][y].team = tile.team
            self.back[x + 1][y].charge += power
        if y + 1 < self.lenght:
            self.back[x][y + 1].team = tile.team
            self.back[x][y + 1].charge += power

        self.back[x][y].team = Team.Neutral
        self.back[x][y].charge = 0

    def copy_front_to_back(self):
        for x in range(self.width):
            for y in range(self.lenght):
                self.back[x][y].pick(self.front[x][y])

    def copy_back_to_front(self):
        for x in range(self.width):
            for y in range(self.lenght):
                self.front[x][y].pick(self.back[x][y])

    def check_tiles(self, tiles_pos: set[tuple]) -> set:
        self.copy_front_to_back()

        update = set()
        for tile_pos in tiles_pos:
            x, y = tile_pos
            if self.front[x][y].charge < 4:
                continue
            self.explode_tile(x, y)
            if x > 0:
                update.add((x - 1, y))
            if y > 0:
                update.add((x, y - 1))
            if x + 1 < self.width:
                update.add((x + 1, y))
            if y + 1 < self.lenght:
                update.add((x, y + 1))

        self.copy_back_to_front()
        return update

    def alive_team(self) -> Team:
        alive = Team.Neutral
        for y in range(self.lenght):
            for x in range(self.width):
                alive |= self.front[x][y].team
        return alive & Team.playable


class Graphic:
    def __init__(self, board: Board, fps: int):
        self.fps = fps
        self.tex_size = 16
        self.team_uv = ((0, 0), (16, 0), (32, 0), (48, 0))

        self.board = board
        self.offset = (
            (pyxel.width - board.width * self.tex_size) // 2,
            (pyxel.height - board.lenght * self.tex_size) // 2
        )

        self.animation = False
        self.duration = 0.25 * fps
        self.time = 0

    def mouse(self, team: Team):
        iteam = -1
        match team:
            case Team.Red: iteam = 0
            case Team.Blue: iteam = 1
            case Team.Green: iteam = 2
            case Team.Yellow: iteam = 3
        pyxel.blt(
            pyxel.mouse_x, pyxel.mouse_y, 0,
            self.tex_size * iteam, 32, self.tex_size, self.tex_size,
            0
        )

    def tile_back(self, pos_x: int | float, pos_y: int | float):
        pyxel.blt(pos_x, pos_y, 0, 64, 0, self.tex_size, self.tex_size)

    def tile_content(self, pos_x: int | float, pos_y: int | float, tile: Tile):
        if tile.team == Team.Neutral:
            return
        iteam = -1
        match tile.team:
            case Team.Red: iteam = 0
            case Team.Blue: iteam = 1
            case Team.Green: iteam = 2
            case Team.Yellow: iteam = 3

        pyxel.blt(
            pos_x, pos_y, 0,
            self.team_uv[iteam][0], self.team_uv[iteam][1],
            self.tex_size, self.tex_size,
            0
        )

        color = 9 if tile.charge > 4 else 13
        pyxel.text(pos_x + 6, pos_y + 6, str(min(tile.charge, 4)), color)
        pyxel.text(pos_x + 6, pos_y + 5, str(min(tile.charge, 4)), 7)

    def board_all(self):
        for y in range(self.board.lenght):
            for x in range(self.board.width):
                pos_x, pos_y = x * self.tex_size + self.offset[0], y * self.tex_size + self.offset[1]
                self.tile_back(pos_x, pos_y)
                self.tile_content(pos_x, pos_y, self.board.front[x][y])

    def board_animate(self):
        for y in range(self.board.lenght):
            for x in range(self.board.width):
                gx, gy = x * self.tex_size + self.offset[0], y * self.tex_size + self.offset[1]
                self.tile_back(gx, gy)

        self.time += 1
        t = self.time / self.duration
        offset = (2 * t - t * t) * self.tex_size
        for y in range(self.board.lenght):
            for x in range(self.board.width):
                gx, gy = x * self.tex_size + self.offset[0], y * self.tex_size + self.offset[1]
                tile = self.board.front[x][y]
                if tile.charge < 4:
                    self.tile_content(gx, gy, tile)
                    continue

                clone = self.board.front[x][y].copy()
                clone.charge = tile.charge - 3
                if x > 0:
                    self.tile_content(gx - offset, gy, clone)
                if y > 0:
                    self.tile_content(gx, gy - offset, clone)
                if x + 1 < self.board.width:
                    self.tile_content(gx + offset, gy, clone)
                if y + 1 < self.board.lenght:
                    self.tile_content(gx, gy + offset, clone)
                del clone, tile

        if self.time >= self.duration:
            self.animation = False
            self.time = 0

    def board_has_4(self) -> bool:
        for y in range(self.board.lenght):
            for x in range(self.board.width):
                if self.board.front[x][y].charge >= 4:
                    return True
        return False

    def win_text(self, team: Team):
        iteam = -1
        match team:
            case Team.Red: iteam = 0
            case Team.Blue: iteam = 1
            case Team.Green: iteam = 2
            case Team.Yellow: iteam = 3
        color = (14, 6, 11, 10)[iteam]
        team_text = ("Red", "Blue", "Green", "Yellow")[iteam]

        x = (pyxel.width - 4 * len(team_text) - 22) // 2
        y = self.offset[1] - 8
        pyxel.text(x, y + 1, team_text + " win !", color)
        pyxel.text(x, y, team_text + " win !", 7)


class ColorWar:
    def __init__(self):
        fps = 75
        pyxel.init(128, 128, display_scale=6, fps=fps, title="Color War")
        pyxel.load("ressources.pyxres")
        pyxel.mouse(False)

        self.board = Board(7, 7)
        self.update_table = set()

        self.turn_order = list(Team.Green | Team.Blue)
        shuffle(self.turn_order)
        self.team_alive = Team.playable
        self.team_playing: Team = self.turn_order[0]
        self.team_index = 0  # index of turn order

        self.first = True
        self.end = False

        self.graphic = Graphic(self.board, fps)

        # AI control
        self.ai_training = False

        pyxel.run(self.update, self.draw)

    def get_mouse_input(self) -> None | tuple:
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return None

        m_x, m_y = pyxel.mouse_x, pyxel.mouse_y
        tile_x = (m_x - self.graphic.offset[0]) // self.graphic.tex_size
        tile_y = (m_y - self.graphic.offset[1]) // self.graphic.tex_size
        if tile_x < 0 or tile_y >= self.board.width or tile_y < 0 or tile_y >= self.board.lenght:
            return None

        return tile_x, tile_y

    def get_action_input(self, action: list | tuple) -> None | tuple:
        best = (0, action[0])
        for value in enumerate(action[1:], start=1):
            if value[1] > best[1]:
                best = value
        return best[0] // self.board.width, best[0] % self.board.width

    def play_on(self, x: int, y: int) -> bool:
        """
        Play on tile with the current team and gamestate
        :param x: position X on the board
        :param y: position Y on the board
        :return: move validity
        """

        tile = self.board.front[x][y]

        tile_camp = 2  # 0: ally, 1: neutral, 2: enemy
        if tile.team == Team.Neutral:
            tile_camp = 1
        elif tile.team == self.team_playing:
            tile_camp = 0

        if not self.first and tile_camp == 1 or tile_camp == 2:
            return False

        tile.team = self.team_playing
        tile.charge = 3 if self.first else tile.charge + 1
        return True

    def update(self):
        if self.end or self.graphic.animation:
            return

        if len(self.update_table) > 0:
            self.update_table = self.board.check_tiles(self.update_table)
            if not self.first:
                self.team_alive = self.board.alive_team()
            if len(self.team_alive) < 2:
                self.end = True
            if len(self.update_table) == 0:
                self.team_index = (self.team_index + 1) % len(self.turn_order)
                self.team_playing = self.turn_order[self.team_index]
            return

        if self.team_playing not in self.team_alive:
            self.team_index = (self.team_index + 1) % len(self.turn_order)
            self.team_playing = self.turn_order[self.team_index]

        tile_pos = self.get_mouse_input()
        if tile_pos is not None and self.play_on(*tile_pos):
            self.update_table.add(tile_pos)

            if self.team_playing == self.turn_order[-1]:
                self.first = False

    def draw(self):
        pyxel.cls(0)

        if self.graphic.animation and not self.end:
            self.graphic.board_animate()
        else:
            self.graphic.board_all()
            self.graphic.animation = self.graphic.board_has_4()

        self.graphic.mouse(self.team_playing)
        if self.end:
            self.graphic.win_text(self.team_playing)


ColorWar()
