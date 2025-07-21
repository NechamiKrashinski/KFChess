import pathlib
from .graphics import Graphics
from .board import Board
from typing import Dict


class GraphicsFactory:
    def load(self,
             sprites_root: pathlib.Path,
             cfg: dict[str, bool],  # למשל {"PB": True, "QW": True}
             board: Board,
             loop: bool = True,
             fps: float = 6.0
             ) -> Dict[str, Dict[str, Graphics]]:
        """
        Load Graphics objects per piece and per state.

        Returns:
            {
              "PB": {
                  "idle": Graphics(...),
                  "move": Graphics(...),
                  ...
              },
              ...
            }
        """
        graphics_map: Dict[str, Dict[str, Graphics]] = {}

        for piece_id in cfg:
            piece_states_dir = sprites_root / piece_id / "states"
            if not piece_states_dir.exists():
                raise FileNotFoundError(f"Missing states folder for {piece_id}: {piece_states_dir}")

            state_graphics = {}

            for state_dir in piece_states_dir.iterdir():
                if not state_dir.is_dir():
                    continue

                sprites_dir = state_dir / "sprites"
                if not sprites_dir.exists():
                    continue

                state_name = state_dir.name
                try:
                    g = Graphics(
                        sprites_folder=sprites_dir,
                        board=board,
                        loop=loop,
                        fps=fps
                    )
                    state_graphics[state_name] = g
                except ValueError as e:
                    # לדלג על state בלי ספרייטים
                    continue

            if not state_graphics:
                raise ValueError(f"No valid states found for piece {piece_id}")

            graphics_map[piece_id] = state_graphics

        return graphics_map
