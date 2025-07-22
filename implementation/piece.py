from .board import Board
from .command import Command
from .state import State
import cv2
import numpy as np


class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """Initialize a piece with ID and initial state."""
        self.piece_id = piece_id
        self._state = init_state
        self._last_command_time = 0

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if self.is_command_possible(cmd, now_ms):
            self._state = self._state.process_command(cmd, now_ms)
            self._last_command_time = now_ms

    def is_command_possible(self, cmd: Command, now_ms: int) -> bool:
        """Determine if the command can be applied now (based on state cooldown)."""
        return self._state.can_transition(now_ms)

    def reset(self, start_ms: int):
        """Reset the piece to its initial state."""
        self._last_command_time = start_ms
        cmd = self._state.get_command()
        if cmd:
            self._state.reset(cmd)

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        self._state = self._state.update(now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        """
        Draw the piece on the board with cooldown overlay.
        """
        self.update(now_ms)

        # קבלת התמונה של הכלי מתוך ה-State
        piece_img = self._state.get_graphics().get_img()
        pos_x, pos_y = self._state.get_physics().get_pos()

        board_x = int(pos_x / board.cell_W_m * board.cell_W_pix)
        board_y = int(pos_y / board.cell_H_m * board.cell_H_pix)

        # ציור הכלי על הלוח באמצעות Img
        piece_img.draw_on(other_img=board.img, x=board_x, y=board_y)
        
        # אם יש Cooldown, לצייר שכבה נוספת
        if not self._state.can_transition(now_ms):
            cooldown_img = piece_img.clone()
            # קבלת המידות של תמונת הכלי הנוכחית
            h, w, _ = cooldown_img.img.shape 
            cv2.rectangle(cooldown_img.img, (0, 0), (w, h), (0, 0, 255), -1)
            cooldown_img.draw_on(other_img=board.img, x=board_x, y=board_y, alpha=0.4)

    def get_physics(self):
        """Get the physics object of the current state."""
        return self._state.get_physics()