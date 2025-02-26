from __future__ import annotations

import pyxel


class Tile:
    def __init__(self, team: int | None = None, charge: int = 0):
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

        self.back[x][y].team = None
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

    def alive_team(self) -> list:
        alive = []
        for y in range(self.lenght):
            for x in range(self.width):
                tile = self.front[x][y]
                if tile.team is None or tile.team in alive:
                    continue
                alive.append(tile.team)
        return sorted(alive)


class Graphic:
    def __init__(self, board: Board):
        self.tex_size = 16
        self.team_uv = ((0, 0), (16, 0), (32, 0), (48, 0))

        self.board = board
        self.offset = (
            (pyxel.width - board.width * self.tex_size) // 2,
            (pyxel.height - board.lenght * self.tex_size) // 2
        )

    def mouse(self, team: int):
        pyxel.blt(
            pyxel.mouse_x, pyxel.mouse_y, 0,
            self.tex_size * team, 32, self.tex_size, self.tex_size,
            0
        )

    def tile_back(self, pos_x: int | float, pos_y: int | float):
        pyxel.blt(pos_x, pos_y, 0, 64, 0, self.tex_size, self.tex_size)

    def tile_content(self, pos_x: int | float, pos_y: int | float, tile_x: int, tile_y: int):
        tile = self.board.front[tile_x][tile_y]
        if tile.team is None:
            return

        pyxel.blt(
            pos_x, pos_y, 0,
            self.team_uv[tile.team][0], self.team_uv[tile.team][1],
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
                self.tile_content(pos_x, pos_y, x, y)


class ColorWar:
    def __init__(self):
        pyxel.init(128, 128, display_scale=6, fps=240, title="Color War")
        pyxel.load("ressources.pyxres")
        pyxel.mouse(False)

        self.board = Board(7, 7)
        self.update_table = set()

        self.team_alive = list(range(4))
        self.team_playing = 0
        self.first = True
        self.end = False
        self.played = False

        self.graphic = Graphic(self.board)

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

    def update(self):
        tile_pos = self.get_mouse_input()
        must_update = len(self.update_table) > 0

        if tile_pos is not None and not must_update:
            tile = self.board.front[tile_pos[0]][tile_pos[1]]

            if self.first and tile.team is None:
                self.board.front[tile_pos[0]][tile_pos[1]].team = self.team_playing
                self.board.front[tile_pos[0]][tile_pos[1]].charge = 3
                self.update_table.add(tile_pos)
                self.team_playing = (self.team_playing + 1) % 4

            elif tile.team == self.team_playing or True:
                self.board.front[tile_pos[0]][tile_pos[1]].team = self.team_playing
                self.board.front[tile_pos[0]][tile_pos[1]].charge += 1
                self.update_table.add(tile_pos)
                self.team_playing = (self.team_playing + 1) % 4

        if must_update:
            self.update_table = self.board.check_tiles(self.update_table)
            if self.team_playing == 3:
                self.first = False

    def draw(self):
        pyxel.cls(0)
        self.graphic.board_all()
        self.graphic.mouse(self.team_playing)


ColorWar()
