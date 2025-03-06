from game.team import Team


class Player:
    def __init__(self):
        self.team = Team.Neutral

    def ready(self) -> bool:
        pass

    def play_on(self) -> tuple[int, int]:
        pass


class Human(Player):
    def ready(self) -> bool:
        return False


class AI(Player):
    def ready(self) -> bool:
        return True
