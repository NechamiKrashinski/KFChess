import logging
import pathlib
import csv
from typing import List, Dict, Tuple, Optional

from .board import Board
from .game import Game
from .piece import Piece
from .piece_factory import PieceFactory
from .img import Img


class GameBuilder:
    def __init__(self, root_folder: pathlib.Path, 
                 board_width: int, board_height: int,
                 cell_width_pix: int, cell_height_pix: int, 
                 board_image_file: str):
        self.root_folder = root_folder.resolve()
        
        board_img = Img()
        board_img_path = self.root_folder / board_image_file
        board_img.read(board_img_path)
        expected_board_width_pix = board_width * cell_width_pix
        expected_board_height_pix = board_height * cell_height_pix
        board_img.resize(expected_board_width_pix, expected_board_height_pix)
        cell_width_m = 0.5
        cell_height_m = 0.5
        self.board = Board(
            cell_H_pix=cell_height_pix,
            cell_W_pix=cell_width_pix,
            cell_H_m=cell_height_m,
            cell_W_m=cell_width_m,
            W_cells=board_width,
            H_cells=board_height,
            img=board_img
        )
        pieces_root_folder = self.root_folder / "pieces_resources"
        self.piece_factory = PieceFactory(self.board, pieces_root_folder)
    
    def _read_board_layout(self, board_file: pathlib.Path) -> List[Tuple[str, Tuple[int, int]]]:
        """Read the board layout from a CSV file that represents the board as a grid."""
        pieces_data = []
        with open(board_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_index, row in enumerate(reader):
                for col_index, piece_type in enumerate(row):
                    piece_type = piece_type.strip()
                    if piece_type:
                        pieces_data.append((piece_type, (col_index, row_index)))
        return pieces_data

    def build_game(self, board_file: str) -> Game:
        """Build the full game by creating all pieces and a Game instance."""
        board_path = self.root_folder / board_file
        if not board_path.exists():
            raise FileNotFoundError(f"Board file not found at {board_path}")

        pieces_data = self._read_board_layout(board_path)
        game_pieces: List[Piece] = []
        
        for piece_type, location in pieces_data:
             piece = self.piece_factory.create_piece(piece_type, location)
             game_pieces.append(piece)

        game = Game(game_pieces, self.board)
        
        return game
