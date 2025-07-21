import pathlib
from typing import Dict, Tuple
import json
from board import Board
from graphicsFactory import GraphicsFactory
from moves import Moves
from physicsFactory import PhysicsFactory
from piece import Piece
from state import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and 
        generates the library of piece templates from the pieces directory.."""
        pass

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        pass

    # PieceFactory.py  – replace create_piece(...)
    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        pass 