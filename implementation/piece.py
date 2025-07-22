import cv2
import numpy as np
from typing import List, Tuple

from .board import Board
from .command import Command
from .state import State
# וודא שהייבוא של Moves נכון לפי מבנה הפרויקט שלך
# from .moves import Moves # או מה שמתאים לך

class Piece:
    def __init__(self, piece_id: str, init_state: State):
        self.piece_id = piece_id
        self._state = init_state
        self._last_command_time = 0

    def on_command(self, cmd: Command, now_ms: int):
        if self.is_command_possible(cmd, now_ms):
            self._state = self._state.process_command(cmd, now_ms)
            self._last_command_time = now_ms

    def is_command_possible(self, cmd: Command, now_ms: int) -> bool:
        return self._state.can_transition(now_ms)

    def reset(self, start_ms: int):
        self._last_command_time = start_ms
        cmd = self._state.get_command()
        if cmd:
            self._state.reset(cmd)

    def update(self, now_ms: int):
        self._state = self._state.update(now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        self.update(now_ms)

        piece_img_obj = self._state.get_graphics().get_img()
        piece_img = piece_img_obj.img

        pos_x_m, pos_y_m = self._state.get_physics().get_pos()

        board_x_pix = int(pos_x_m / board.cell_W_m * board.cell_W_pix)
        board_y_pix = int(pos_y_m / board.cell_H_m * board.cell_H_pix)

        h_piece, w_piece, _ = piece_img.shape

        board_width_pix = board.W_cells * board.cell_W_pix
        board_height_pix = board.H_cells * board.cell_H_pix

        draw_x = max(0, min(board_x_pix, board_width_pix - w_piece))
        draw_y = max(0, min(board_y_pix, board_height_pix - h_piece))

        if board_x_pix < 0 or board_y_pix < 0 or \
           board_x_pix + w_piece > board_width_pix or \
           board_y_pix + h_piece > board_height_pix:
            print(f"Warning: Piece drawing for {self.piece_id} at ({board_x_pix}, {board_y_pix}) exceeds board dimensions.")

        piece_img_obj.draw_on(other_img=board.img, x=draw_x, y=draw_y)

        if not self._state.can_transition(now_ms):
            cooldown_img = piece_img_obj.clone()
            h, w, _ = cooldown_img.img.shape
            cv2.rectangle(cooldown_img.img, (0, 0), (w, h), (0, 0, 255), -1)
            cooldown_img.draw_on(other_img=board.img, x=draw_x, y=draw_y, alpha=0.4)

    def get_physics(self):
        return self._state.get_physics()

    def get_moves(self, occupied_cells: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        current_cell = self.get_physics().get_cell()

        moves_logic = self._state.get_moves()

        # קבע אם הכלי הנוכחי יכול לדלג (מלכה לא יכולה, פרש כן)
        can_this_piece_jump = (self.piece_id[0].upper() == 'N') # 'N' for Knight (פרש)

        valid_moves = moves_logic.get_moves(
            r=current_cell[0],
            c=current_cell[1],
            occupied_cells=occupied_cells, # רשימת התאים התפוסים מועברת ל-Moves
            can_jump=can_this_piece_jump,
            allow_capture=True
        )

        return valid_moves