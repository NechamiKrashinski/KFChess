import pathlib
from typing import List, Tuple

class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        self.dims = dims
        self.moves_all: List[Tuple[int, int, str]] = []

        with open(moves_txt_path, 'r') as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                if ":" in stripped:
                    coord_part, move_type = stripped.split(":")
                else:
                    coord_part, move_type = stripped, "normal"

                parts = coord_part.split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid move line (expected 'dx,dy[:desc]'): '{stripped}'")

                try:
                    dx = int(parts[0])
                    dy = int(parts[1])
                    self.moves_all.append((dx, dy, move_type))
                except ValueError:
                    raise ValueError(f"Invalid integers in move line: '{stripped}'")

    def get_moves(self,
              r: int,
              c: int,
              occupied_cells: List[Tuple[int, int]],
              can_jump: bool = False,
              allow_capture: bool = False) -> List[Tuple[int, int]]:

        rows, cols = self.dims
        valid = []

        for dx, dy, move_type in self.moves_all:
            nr, nc = r + dx, c + dy
            target_cell = (nr, nc)

            # 1. בדיקת גבולות הלוח
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue

            is_target_occupied = target_cell in occupied_cells

            # 2. האם מדובר בחייל? (move_type מוגדר לפי קובץ החיילים)
            is_pawn = move_type in ("non_capture", "capture", "1st")

            if is_pawn:
                if move_type == "non_capture":
                    if is_target_occupied:
                        continue  # לא יכול לזוז לתא תפוס
                elif move_type == "capture":
                    if not allow_capture or not is_target_occupied:
                        continue  # חייב להיות תא תפוס והרשאה ללכוד
                elif move_type == "1st":
                    if is_target_occupied:
                        continue  # תנועה קדמית בתחילת המשחק – רק אם פנוי
                else:
                    continue  # move_type לא מוכר

            else:
                # כלי רגיל: תמיד יכול לאכול תא תפוס
                # אין צורך ב־move_type – פשוט:
                pass  # כל מקרה עובר

            # 3. בדיקת חסימה בדרך – רק אם הכלי לא יכול לקפוץ
            if not can_jump and self._is_straight_move(dx, dy):
                if self._is_path_blocked((r, c), target_cell, occupied_cells):
                    continue

            valid.append(target_cell)

        return valid


    def _is_straight_move(self, dx: int, dy: int) -> bool:
        """Determines if a move (dx, dy) represents a straight line (horizontal, vertical, or diagonal)."""
        return dx == 0 or dy == 0 or abs(dx) == abs(dy)

    def _is_path_blocked(self,
                         start_cell: Tuple[int, int],
                         end_cell: Tuple[int, int],
                         occupied_cells: List[Tuple[int, int]]) -> bool:
        print(f"DEBUG: Checking path from {start_cell} to {end_cell}")
        print(f"DEBUG: Occupied cells: {occupied_cells}")
        
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
            print(f"DEBUG: Checking intermediate cell: {intermediate_cell}")

            if intermediate_cell in occupied_cells:
                print(f"DEBUG: Path BLOCKED at {intermediate_cell}")
                return True
        print(f"DEBUG: Path CLEAR")
        return False