import pathlib
from typing import List, Tuple, Dict

class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        self.dims = dims
        self.raw_moves: Dict[str, List[Tuple[int, int, str]]] = self._load_moves(moves_txt_path)

    def _load_moves(self, moves_txt_path: pathlib.Path) -> Dict[str, List[Tuple[int, int, str]]]:
        return {}  # Not loading anything at this stage.

    def get_moves(self,
                  r: int,
                  c: int,
                  all_occupied_cells: List[Tuple[int, int]],
                  occupied_enemy_cells: List[Tuple[int, int]],
                  can_jump: bool,  # Only for knight
                  piece_type: str,  # e.g., 'P', 'R', 'N', 'B', 'Q', 'K'
                  my_color: str     # 'W' or 'B'
                  ) -> List[Tuple[int, int]]:

        rows, cols = self.dims
        valid_moves: List[Tuple[int, int]] = []

        def _is_valid_cell(cell: Tuple[int, int]) -> bool:
            x, y = cell
            return 0 <= x < rows and 0 <= y < cols

        if piece_type == 'P':  # Pawn
            direction = -1 if my_color == 'W' else 1

            forward_one_cell = (r, c + direction)
            if _is_valid_cell(forward_one_cell) and forward_one_cell not in all_occupied_cells:
                valid_moves.append(forward_one_cell)

            start_row = 6 if my_color == 'W' else 1
            if c == start_row:
                forward_two_cell = (r, c + 2 * direction)
                if _is_valid_cell(forward_two_cell) and \
                   forward_one_cell not in all_occupied_cells and \
                   forward_two_cell not in all_occupied_cells:
                    valid_moves.append(forward_two_cell)

            capture_diag_left = (r - 1, c + direction)
            capture_diag_right = (r + 1, c + direction)

            for target_cell in [capture_diag_left, capture_diag_right]:
                if _is_valid_cell(target_cell) and target_cell in occupied_enemy_cells:
                    valid_moves.append(target_cell)

        elif piece_type == 'N':  # Knight
            knight_offsets = [
                (1, 2), (1, -2), (-1, 2), (-1, -2),
                (2, 1), (2, -1), (-2, 1), (-2, -1)
            ]
            for dx, dy in knight_offsets:
                target_cell = (r + dx, c + dy)
                if _is_valid_cell(target_cell):
                    if target_cell not in all_occupied_cells:
                        valid_moves.append(target_cell)
                    elif target_cell in occupied_enemy_cells:
                        valid_moves.append(target_cell)

        elif piece_type in ['R', 'B', 'Q', 'K']:  # Rook, Bishop, Queen, King
            directions: List[Tuple[int, int]] = []
            if piece_type == 'R' or piece_type == 'Q':
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if piece_type == 'B' or piece_type == 'Q':
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            if piece_type == 'K':
                directions.extend([
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ])

            for dr, dc in directions:
                max_steps = 1 if piece_type == 'K' else max(rows, cols)

                for i in range(1, max_steps + 1):
                    target_cell = (r + dr * i, c + dc * i)

                    if not _is_valid_cell(target_cell):
                        break

                    if target_cell in all_occupied_cells:
                        if target_cell in occupied_enemy_cells:
                            valid_moves.append(target_cell)
                        break

                    else:
                        valid_moves.append(target_cell)

        return valid_moves

    def _is_straight_move(self, dx: int, dy: int) -> bool:
        """Determines if a move (dx, dy) represents a straight line."""
        return dx == 0 or dy == 0 or abs(dx) == abs(dy)

    def _is_path_blocked(self,
                          start_cell: Tuple[int, int],
                          end_cell: Tuple[int, int],
                          occupied_cells: List[Tuple[int, int]]) -> bool:
        start_row, start_col = start_cell
        end_row, end_col = end_cell

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        step_row = 0
        if delta_row > 0:
            step_row = 1
        elif delta_row < 0:
            step_row = -1

        step_col = 0
        if delta_col > 0:
            step_col = 1
        elif delta_col < 0:
            step_col = -1

        steps = max(abs(delta_row), abs(delta_col))

        for i in range(1, steps):
            intermediate_row = start_row + i * step_row
            intermediate_col = start_col + i * step_col
            intermediate_cell = (intermediate_row, intermediate_col)

            if intermediate_cell in occupied_cells:
                return True
        return False
