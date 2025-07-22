import pathlib
import json
from .graphics import Graphics
from .board import Board

class GraphicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def load(self, sprites_dir: pathlib.Path, cfg: dict) -> Graphics:
        """Loads graphics from a sprites directory using the provided configuration."""
        if not sprites_dir.is_dir():
            raise FileNotFoundError(f"Sprites directory not found: {sprites_dir}")

        graphics_cfg = cfg.get("graphics", {})
        fps = graphics_cfg.get("frames_per_sec", 6)
        is_loop = graphics_cfg.get("is_loop", False)

        return Graphics(
            sprites_folder=sprites_dir,
            board=self.board,
            loop=is_loop,
            fps=fps
        )
