import pathlib
from typing import Dict, Tuple
import json

from .board import Board
from .graphics_factory import GraphicsFactory
from .physics_factory import PhysicsFactory
from .piece import Piece
from .state import State
from .moves import Moves


class PieceFactory:
    """
    Factory that creates Piece objects based on configurations and resources
    in a pieces directory. Each piece is defined by a folder that includes
    a config.json and sprite resources per state.
    """

    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root.resolve()
        self.templates: Dict[str, dict] = {}
        self.graphics_factory = GraphicsFactory()
        self.physics_factory = PhysicsFactory(board)
        self._load_piece_templates()

    def _load_piece_templates(self):
        for piece_dir in self.pieces_root.iterdir():
            if not piece_dir.is_dir():
                continue
            config_path = piece_dir / "config.json"
            if not config_path.exists():
                continue
            with open(config_path, 'r') as f:
                cfg = json.load(f)
                self.templates[piece_dir.name] = {
                    "cfg": cfg,
                    "dir": piece_dir
                }

    def _build_state_machine(self, piece_dir: pathlib.Path, cfg: dict, cell: Tuple[int, int]) -> State:
        if "moves" not in cfg:
            raise KeyError("Missing 'moves' in config")

        graphics_map = self.graphics_factory.load(
            sprites_root=self.pieces_root,
            cfg={cfg["id"]: True},
            board=self.board
        )[cfg["id"]]

        moves_txt_path = piece_dir / cfg["moves"]
        dims = (self.board.H_cells, self.board.W_cells)
        moves = Moves(moves_txt_path, dims)

        physics = self.physics_factory.create(cell, cfg.get("physics", {}))
        default_state_name = next(iter(graphics_map))
        main_state = State(
            moves=moves,
            graphics=graphics_map[default_state_name],
            physics=physics
        )

        transitions_cfg = cfg.get("transitions", {})
        for from_state, events in transitions_cfg.items():
            for event_name, to_state in events.items():
                if to_state in graphics_map:
                    target_state = State(
                        moves=moves,
                        graphics=graphics_map[to_state],
                        physics=physics
                    )
                    if from_state == default_state_name:
                        main_state.set_transition(event_name, target_state)

        return main_state

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        if p_type not in self.templates:
            raise ValueError(f"Unknown piece type: {p_type}")

        entry = self.templates[p_type]
        cfg = entry["cfg"]
        piece_dir = entry["dir"]

        state = self._build_state_machine(piece_dir, cfg, cell)
        return Piece(cfg["id"], state)
