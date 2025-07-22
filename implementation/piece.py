import cv2
import numpy as np
from typing import List, Tuple

from .board import Board
from .command import Command
from .state import State


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
        """
        Draw the piece on the board with cooldown overlay.
        """
        self.update(now_ms)

        piece_img_obj = self._state.get_graphics().get_img()
        piece_img = piece_img_obj.img # Get the actual numpy array for dimensions
        
        pos_x_m, pos_y_m = self._state.get_physics().get_pos()

        # Convert meters to pixels. Assuming pos_x_m, pos_y_m are top-left of the piece's bounding box.
        # Ensure that board.cell_W_pix and board.cell_H_pix are the pixel dimensions for a single cell.
        board_x_pix = int(pos_x_m / board.cell_W_m * board.cell_W_pix)
        board_y_pix = int(pos_y_m / board.cell_H_m * board.cell_H_pix)
        
        # Get piece image dimensions
        h_piece, w_piece, _ = piece_img.shape

        # Calculate bounding box on the board
        board_width_pix = board.W_cells * board.cell_W_pix
        board_height_pix = board.H_cells * board.cell_H_pix

        # Ensure the piece is drawn within board boundaries.
        # Adjust x, y if piece would go out of bounds
        draw_x = max(0, min(board_x_pix, board_width_pix - w_piece))
        draw_y = max(0, min(board_y_pix, board_height_pix - h_piece))

        # Check for drawing exceeding board dimensions and print a warning
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
        all_moves = self._state.get_moves().moves_all 
        rows, cols = self._state.get_physics().board.H_cells, self._state.get_physics().board.W_cells 
        valid = [] 

        for dx, dy, move_type in all_moves: 
            print(f"[DEBUG] Checking move: dx={dx}, dy={dy}, type={move_type}")
            nr = current_cell[0] + dx 
            nc = current_cell[1] + dy 
            if not (0 <= nr < rows and 0 <= nc < cols): 
                continue 

            dest = (nr, nc) 
            if move_type == "capture": 
                if dest in occupied_cells: 
                    valid.append(dest) 
            else: 
                if dest not in occupied_cells: 
                    valid.append(dest) 

        return valid