class Piece:
    def __init__(self, piece_id: str, init_state: State):
        pass

    def on_command(self, cmd: Command, now_ms: int):
        pass

    def is_command_possible(self, cmd: Command, now_ms: int) -> bool:
        pass

    def reset(self, start_ms: int):
        pass

    def update(self, now_ms: int):
        pass

    def draw_on_board(self, board: Board, now_ms: int):
        pass

    def get_physics(self):
        pass

    def get_moves(self, all_pieces: List['Piece']) -> List[Tuple[int, int]]:
        pass
