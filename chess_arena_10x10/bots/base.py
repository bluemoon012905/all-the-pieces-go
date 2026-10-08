class BaseBot:
    def __init__(self, color):
        self.color = color

    def get_move(self, board_state):
        raise NotImplementedError

