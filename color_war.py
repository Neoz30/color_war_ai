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

    def swap(self):
        """
        Swap the board and the buffer state
        board become buffer and buffer become board
        """
        tmp = self.front
        self.front = self.back
        self.back = tmp
        del tmp

    def update(self, tile_x: int, tile_y: int):
        tile = self.front[tile_x][tile_y]
        if tile.team is None or tile.charge < 4:
            pass
            return

        inc = tile.charge - 3  # Add the bomb chain bug
        for offset in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            side_x, side_y = tile_x + offset[0], tile_y + offset[1]
            if not (0 <= side_x < self.width and 0 <= side_y < self.lenght):
                continue

            self.back[side_x][side_y].charge += inc
            self.back[side_x][side_y].team = tile.team

        # Clear current tile
        self.back[tile_x][tile_y].team = None
        self.back[tile_x][tile_y].charge = 0

    def turn(self):
        for y in range(self.lenght):
            for x in range(self.width):
                self.update(x, y)

        # Swap buffer and board (almost like copying it)
        self.swap()

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

    def mouse(self, team):
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
        pyxel.init(128, 128, display_scale=6, fps=60)
        pyxel.load("ressources.pyxres")
        pyxel.mouse(False)

        self.board = Board(7, 7)
        self.gamestate = 0
        self.team_alive = list(range(1, 5))
        self.team_playing = 1

        self.graphic = Graphic(self.board)

        self.board.back[1][1].team = 0
        self.board.back[1][1].charge = 3

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
        if tile_pos is not None:
            self.board.back[tile_pos[0]][tile_pos[1]].team = 0
            self.board.back[tile_pos[0]][tile_pos[1]].charge += 1

        match self.gamestate:
            case 0:
                pass
            case 1:
                pass
            case _:
                pass
        self.board.turn()

    def draw(self):
        pyxel.cls(0)
        self.graphic.board_all()
        self.graphic.mouse(0)


ColorWar()
