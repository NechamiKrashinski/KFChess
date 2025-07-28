import pathlib
import csv
from typing import List, Tuple, Dict

from implementation.publish_subscribe.message_display import MessageDisplay
from implementation.publish_subscribe.move_logger_display import MoveLoggerDisplay

from .board import Board
from .game import Game
from .piece import Piece
from .piece_factory import PieceFactory
from .img import Img
from .publish_subscribe.event_manager import EventManager

class GameBuilder:
    def __init__(self, root_folder: pathlib.Path, 
                 board_width: int, board_height: int,
                 cell_width_pix: int, cell_height_pix: int, 
                 board_image_file: str,
                 background_image_file: str,
                 screen_width: int, 
                 screen_height: int):
        
        self.root_folder = root_folder.resolve()
        self.screen_width = screen_width
        self.screen_height = screen_height

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

        self.background_img = Img()
        background_img_path = self.root_folder / background_image_file
        self.background_img.read(background_img_path)
        self.background_img.resize(self.screen_width, self.screen_height)

        pieces_root_folder = self.root_folder / "pieces_resources"
        self.piece_factory = PieceFactory(self.board, pieces_root_folder)
        
        self.event_manager = EventManager() 
        self.move_logger_display = MoveLoggerDisplay(self.event_manager)
        self.message_display = MessageDisplay(self.event_manager)

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
        
        piece_prototypes: Dict[str, Piece] = {}

        for piece_type, location in pieces_data:
            if piece_type not in piece_prototypes:
                prototype_piece = self.piece_factory.create_piece(piece_type, location)
                piece_prototypes[piece_type] = prototype_piece
            
            piece = self.piece_factory.create_piece(piece_type, location)
            game_pieces.append(piece)

        game = Game(game_pieces, self.board, self.event_manager, self.background_img, move_logger_display=self.move_logger_display, message_display=self.message_display) 
        game.screen_width = self.screen_width
        game.screen_height = self.screen_height
        return game