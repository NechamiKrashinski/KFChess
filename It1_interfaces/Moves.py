class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        pass

    def get_moves(self,
                  r: int,
                  c: int,
                  all_occupied_cells: List[Tuple[int, int]],
                  occupied_enemy_cells: List[Tuple[int, int]],
                  can_jump: bool,
                  piece_type: str,
                  my_color: str) -> List[Tuple[int, int]]:
        pass

    def _is_straight_move(self, dx: int, dy: int) -> bool:
        pass

    def _is_path_blocked(self,
                          start_cell: Tuple[int, int],
                          end_cell: Tuple[int, int],
                          occupied_cells: List[Tuple[int, int]]) -> bool:
        pass
