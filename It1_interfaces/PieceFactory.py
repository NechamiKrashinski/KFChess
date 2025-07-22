class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        pass

    def _load_piece_templates(self):
        pass

    def _build_state_machine(self,
                             piece_dir: pathlib.Path,
                             piece_type: str,
                             initial_state_name: str,
                             state_names: List[str]) -> State:
        pass

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        pass
