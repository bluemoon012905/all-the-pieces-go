class BaseBot:
    def __init__(self, color):
        self.color = color

    def get_move(self, board_state):
        raise NotImplementedError

    def get_action(self, game_state):
        """Return a move or a richer engine action such as pass/drop."""

        return self.get_move(game_state)

