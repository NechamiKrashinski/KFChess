import cv2
import numpy as np
from typing import List, Tuple
import logging # <-- תיקון: ייבוא נכון של מודול הלוגינג

from .board import Board
from .command import Command
from .state import State
from .moves import Moves

# הגדרת הלוגר עבור מודול Piece
logger = logging.getLogger(__name__)
# אם עדיין לא הגדרת את basicConfig בקובץ הראשי שמפעיל את המשחק,
# אפשר להשאיר את השורה הבאה. אם היא מוגדרת במקום אחר, עדיף להסיר אותה מכאן.
# logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

class Piece:
    def __init__(self, piece_id: str, init_state: State):
        self.piece_id = piece_id
        self._state = init_state # <-- המשתנה המאחסן את המצב הנוכחי של הכלי
        self._last_command_time = 0
        # logger.info(f"Piece '{self.piece_id}' initialized in state: {self._state.get_graphics().sprites_folder.parent.name}")

    def on_command(self, cmd: Command, now_ms: int):
        if self.is_command_possible(cmd, now_ms):
            # לוגיקה זו כבר הייתה נכונה עם self._state
            self._state = self._state.process_command(cmd, now_ms)
            self._last_command_time = now_ms

    def is_command_possible(self, cmd: Command, now_ms: int) -> bool:
        return self._state.can_transition(now_ms)

    def reset(self, start_ms: int):
        self._last_command_time = start_ms
        cmd = self._state.get_command()
        if cmd:
            self._state.reset(cmd)

    def update(self, dt: float): # <--- חובה לשנות ל-dt: float
        """
        Updates the piece's current state based on the time delta.
        """
        prev_state_name = self._state.get_graphics().sprites_folder.parent.name
        
        # העברת dt למצב הנוכחי! זה קריטי!
        self._state = self._state.update(dt) 

        new_state_name = self._state.get_graphics().sprites_folder.parent.name
        if prev_state_name != new_state_name:
            logger.debug(f"[{self.piece_id}] State transitioned from '{prev_state_name}' to '{new_state_name}'.")


    def draw_on_board(self, board: Board, now_ms: int):
        piece_img_obj = self._state.get_graphics().get_img()
        piece_img = piece_img_obj.img

        pos_x_m, pos_y_m = self._state.get_physics().get_pos()

        board_x_pix = round(pos_x_m / board.cell_W_m * board.cell_W_pix)
        board_y_pix = round(pos_y_m / board.cell_H_m * board.cell_H_pix)

        h_piece, w_piece, _ = piece_img.shape

        board_width_pix = board.W_cells * board.cell_W_pix
        board_height_pix = board.H_cells * board.cell_H_pix

        draw_x = max(0, min(board_x_pix, board_width_pix - w_piece))
        draw_y = max(0, min(board_y_pix, board_height_pix - h_piece))

        if board_x_pix < 0 or board_y_pix < 0 or \
           board_x_pix + w_piece > board_width_pix or \
           board_y_pix + h_piece > board_height_pix:
            # שימוש בלוגר במקום print
            logger.warning(f"Warning: Piece drawing for {self.piece_id} at ({board_x_pix}, {board_y_pix}) exceeds board dimensions.")
        piece_img_obj.draw_on(other_img=board.img, x=draw_x, y=draw_y)

        if not self._state.can_transition(now_ms):
            cooldown_img = piece_img_obj.copy()
            h, w, _ = cooldown_img.img.shape
            cv2.rectangle(cooldown_img.img, (0, 0), (w, h), (0, 0, 255), -1)
            cooldown_img.draw_on(other_img=board.img, x=draw_x, y=draw_y, alpha=0.4)

    def get_physics(self):
        return self._state.get_physics()

    def get_moves(self, all_pieces: List['Piece']) -> List[Tuple[int, int]]:
        current_cell = self.get_physics().get_cell()
        moves_logic = self._state.get_moves()

        piece_type_char = self.piece_id[0].upper() 
        
        can_this_piece_jump = (piece_type_char == 'N') 
        
        my_color = self.piece_id[1].upper() 

        all_occupied_cells: List[Tuple[int, int]] = []
        occupied_enemy_cells: List[Tuple[int, int]] = []

        for p in all_pieces:
            if p.piece_id != self.piece_id: 
                cell_p = p.get_physics().get_cell()
                all_occupied_cells.append(cell_p) 

                if p.piece_id[1].upper() != my_color: 
                    occupied_enemy_cells.append(cell_p) 

        valid_moves = moves_logic.get_moves(
            r=current_cell[0],
            c=current_cell[1],
            all_occupied_cells=all_occupied_cells,
            occupied_enemy_cells=occupied_enemy_cells,
            can_jump=can_this_piece_jump,
            piece_type=piece_type_char, 
            my_color=my_color
        )

        return valid_moves
    
    # המתודה on_command היא זו שעברה את התיקונים העיקריים
    def on_command(self, cmd: Command, now_ms: int):
        """
        Receives a command and passes it to the current state for processing.
        Updates the piece's current state based on the state's response.
        """
        # logger.info(f"[{self.piece_id}] Piece received command: {cmd.type} at {now_ms}ms. Current state: {self._state.get_graphics().sprites_folder.parent.name}")
        
        # זה המקום שבו המצב החדש מוחזר ומשנה את מצב הכלי!
        new_state = self._state.process_command(cmd, now_ms)
        
        if new_state is not self._state:
            # logger.debug(f"[{self.piece_id}] Piece's state transitioned from '{self._state.get_graphics().sprites_folder.parent.name}' to '{new_state.get_graphics().sprites_folder.parent.name}' by command '{cmd.type}'.")
            self._state = new_state
        # else:
            # logger.debug(f"[{self.piece_id}] State '{self._state.get_graphics().sprites_folder.parent.name}' did not change after command '{cmd.type}'.")