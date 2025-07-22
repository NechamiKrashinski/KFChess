class Game:
    def __init__(self, pieces: List[Piece], board: Board): pass
    def game_time_ms(self) -> int: pass
    def clone_board(self) -> Board: pass
    def start_user_input_thread(self): pass
    def run(self): pass
    def _mouse_callback(self, event, x, y, flags, param): pass
    def _process_input(self, cmd: Command, now_ms: int): pass
    def _draw(self, now_ms: int): pass
    def _show(self) -> bool: pass
    def _is_win(self) -> bool: pass
    def _announce_win(self): pass
    def _get_all_pieces_on_board(self) -> List['Piece']: pass
    def _get_all_kings_on_board(self) -> Dict[str, Piece]: pass
