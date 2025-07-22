import pathlib
from typing import List, Tuple

class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        """
        Initialize moves from the moves.txt file and board dimensions.

        Supports both formats:
        - "dx,dy"
        - "dx,dy:description"

        Args:
            moves_txt_path (pathlib.Path): path to the moves.txt file
            dims (Tuple[int, int]): (rows, cols) of the board
        """
        self.dims = dims
        self.move_offsets: List[Tuple[int, int]] = []

        print(f"[DEBUG] Trying to open moves.txt at path: {moves_txt_path}")
        print(f"[DEBUG] Absolute path to moves.txt: {moves_txt_path.resolve()}")
        print(f"[DEBUG] File exists? {moves_txt_path.exists()}")

        with open(moves_txt_path, 'r') as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                # תומך גם בפורמט בלי תיאור
                if ":" in stripped:
                    coord_part = stripped.split(":")[0]
                else:
                    coord_part = stripped

                parts = coord_part.split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid move line (expected 'dx,dy[:desc]'): '{stripped}'")

                try:
                    dx = int(parts[0])
                    dy = int(parts[1])
                    self.move_offsets.append((dx, dy))
                except ValueError:
                    raise ValueError(f"Invalid integers in move line: '{stripped}'")

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        rows, cols = self.dims
        valid_moves = []
        for dx, dy in self.move_offsets:
            nr, nc = r + dx, c + dy
            if 0 <= nr < rows and 0 <= nc < cols:
                valid_moves.append((nr, nc))
        return valid_moves
