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
        """Draw the piece on the board with cooldown overlay if applicable."""
        self.update(now_ms)

        img = self._state.get_graphics().get_img()
        pos_x, pos_y = self._state.get_physics().get_pos()

        board_x = int(pos_x / board.cell_W_m * board.cell_W_pix)
        board_y = int(pos_y / board.cell_H_m * board.cell_H_pix)

        h, w = img.img.shape[:2]
        H, W = board.img.img.shape[:2]

        if board_y + h > H or board_x + w > W:
            raise ValueError("Image drawing exceeds board dimensions.")

        # Draw the piece on the board
        roi = board.img.img[board_y:board_y + h, board_x:board_x + w]
        board.img.img[board_y:board_y + h, board_x:board_x + w] = cv2.add(roi, img.img)

        # Apply cooldown overlay if transition not allowed
        if not self._state.can_transition(now_ms):
            overlay = img.img.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
            alpha = 0.4
            blended = cv2.addWeighted(roi, 1 - alpha, overlay, alpha, 0)
            board.img.img[board_y:board_y + h, board_x:board_x + w] = blended
