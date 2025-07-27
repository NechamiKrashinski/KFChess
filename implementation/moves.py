import pathlib
from typing import List, Tuple, Dict
import math

class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        # dims should be (num_cols, num_rows) -> (8, 8) for standard chess
        self.dims = dims
        self.raw_moves: Dict[str, List[Tuple[int, int, str]]] = self._load_moves(moves_txt_path)

    def _load_moves(self, moves_txt_path: pathlib.Path) -> Dict[str, List[Tuple[int, int, str]]]:
        # This method is not used for the logic, so it can remain a placeholder
        # if you don't load moves from a file.
        return {}

    def _is_valid_cell(self, cell: Tuple[int, int]) -> bool:
        """Helper to check if a cell (col_idx, row_idx) is within board boundaries."""
        col_idx, row_idx = cell
        num_cols, num_rows = self.dims
        return 0 <= col_idx < num_cols and 0 <= row_idx < num_rows

    def _is_straight_move(self, dr: int, dc: int) -> bool:
        """
        Checks if a move (dr, dc) is a straight line (horizontal, vertical, or diagonal).
        dr = change in column, dc = change in row.
        """
        return dr == 0 or dc == 0 or abs(dr) == abs(dc)

    def _is_path_blocked(self, start_cell: Tuple[int, int], end_cell: Tuple[int, int], occupied_cells: List[Tuple[int, int]]) -> bool:
        """
        Checks if the path between start_cell and end_cell is blocked by any occupied_cells.
        Assumes start_cell and end_cell are valid and the move is straight.
        The end_cell itself does not count as a block.
        """
        start_r, start_c = start_cell  # start_r is col, start_c is row
        end_r, end_c = end_cell       # end_r is col, end_c is row

        # If it's a "no move" or one-step move, there are no intermediate cells to block
        if start_cell == end_cell or \
           (abs(start_r - end_r) <= 1 and abs(start_c - end_c) <= 1):
            return False

        dr = end_r - start_r
        dc = end_c - start_c

        # Determine the step direction for each axis
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

        # Iterate through intermediate cells
        current_r, current_c = start_r, start_c
        while True:
            current_r += step_r
            current_c += step_c

            # If we reached or passed the end_cell, the path is not blocked
            if current_r == end_r and current_c == end_c:
                return False

            # Check if the current intermediate cell is occupied
            if (current_r, current_c) in occupied_cells:
                return True

            # If it's a diagonal move and one coordinate reaches its end before the other,
            # it means the path is not perfectly straight (or an error in calling).
            # This check can be useful if _is_straight_move is not perfectly reliable or used.
            # For a perfectly straight line (horizontal, vertical, diagonal),
            # both coordinates should reach the end simultaneously.
            if step_r != 0 and (current_r - start_r) / dr > 1: return False
            if step_c != 0 and (current_c - start_c) / dc > 1: return False

        return False # Should not be reached

    def get_moves(self,
                  r: int, # This is actually column index based on tests
                  c: int, # This is actually row index based on tests
                  all_occupied_cells: List[Tuple[int, int]],
                  occupied_enemy_cells: List[Tuple[int, int]],
                  can_jump: bool,  # Only for knight
                  piece_type: str,  # e.g., 'P', 'R', 'N', 'B', 'Q', 'K'
                  my_color: str    # 'W' or 'B'
                  ) -> List[Tuple[int, int]]:

        num_cols, num_rows = self.dims # Assuming dims are (cols, rows)
        valid_moves: List[Tuple[int, int]] = []

        # Pawn movement
        if piece_type == 'P':
            # White pawns move "up" (decreasing row index 'c')
            # Black pawns move "down" (increasing row index 'c')
            row_direction = -1 if my_color == 'W' else 1
            
            # --- One step forward ---
            # Moves change the row index (c)
            forward_one_cell = (r, c + row_direction)
            if self._is_valid_cell(forward_one_cell) and forward_one_cell not in all_occupied_cells:
                valid_moves.append(forward_one_cell)

                # --- Two steps forward (only from initial row and if both cells are empty) ---
                # Initial rows for pawns (index 'c')
                # White pawns start at c = 6 (assuming 8x8 board where rows are 0-7)
                # Black pawns start at c = 1 (assuming 8x8 board where rows are 0-7)
                initial_row_white = num_rows - 2 # For 8x8, this is 6
                initial_row_black = 1
                
                if (my_color == 'W' and c == initial_row_white) or \
                   (my_color == 'B' and c == initial_row_black):
                    forward_two_cell = (r, c + 2 * row_direction)
                    # Check that the intermediate cell is also not blocked
                    intermediate_cell = (r, c + row_direction)
                    if self._is_valid_cell(forward_two_cell) and \
                       forward_two_cell not in all_occupied_cells and \
                       intermediate_cell not in all_occupied_cells: # Ensure path for 2 steps is clear
                        valid_moves.append(forward_two_cell)

            # --- Captures (diagonal moves) ---
            # Captures change both column (r) and row (c)
            capture_diag_left = (r - 1, c + row_direction)
            capture_diag_right = (r + 1, c + row_direction)

            for target_cell in [capture_diag_left, capture_diag_right]:
                if self._is_valid_cell(target_cell) and target_cell in occupied_enemy_cells:
                    valid_moves.append(target_cell)

        # Knight movement
        elif piece_type == 'N':
            knight_offsets = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_offsets: # dr changes column (r), dc changes row (c)
                target_cell = (r + dr, c + dc)
                if self._is_valid_cell(target_cell):
                    if target_cell not in all_occupied_cells or target_cell in occupied_enemy_cells:
                        valid_moves.append(target_cell)

        # Rook, Bishop, Queen, King movement
        elif piece_type in ['R', 'B', 'Q', 'K']:
            directions: List[Tuple[int, int]] = []
            if piece_type == 'R' or piece_type == 'Q':
                # Rook moves: change only r OR only c
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if piece_type == 'B' or piece_type == 'Q':
                # Bishop moves: change both r AND c by the same absolute amount
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            if piece_type == 'K':
                # King moves: all 8 directions, but only 1 step
                directions = [
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ]

            for dr, dc in directions: # dr changes column (r), dc changes row (c)
                max_steps = 1 if piece_type == 'K' else max(num_rows, num_cols)

                for i in range(1, max_steps + 1):
                    target_cell = (r + dr * i, c + dc * i)

                    if not self._is_valid_cell(target_cell):
                        break

                    # Check if the path is blocked by a friendly piece (not including target cell itself for capture logic)
                    if (target_cell not in occupied_enemy_cells) and (target_cell in all_occupied_cells):
                        break # Cannot move through or land on a friendly piece

                    # If the target cell is occupied by an enemy, it's a valid capture, but stop path
                    if target_cell in occupied_enemy_cells:
                        # Make sure there are no pieces *between* the start and target_cell
                        if not self._is_path_blocked((r, c), target_cell, all_occupied_cells):
                            valid_moves.append(target_cell)
                        break # Stop here, cannot go past an enemy piece

                    # If the target cell is empty, and the path is clear
                    if not self._is_path_blocked((r, c), target_cell, all_occupied_cells):
                        valid_moves.append(target_cell)
                    else:
                        # Path is blocked by an intermediate piece (friendly or enemy that's not the target)
                        break
        return valid_moves