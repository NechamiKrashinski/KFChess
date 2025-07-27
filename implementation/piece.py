import cv2
import numpy as np
from typing import List, Tuple

from .board import Board
from .command import Command
from .state import State
from .moves import Moves

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
        prev_state_name = self._state.get_graphics().sprites_folder.parent.name
        # print(f"[{self.piece_id}] Before update: Current state is {prev_state_name}, Graphics loop: {self._state.get_graphics().loop}, Graphics finished: {self._state.get_graphics().is_finished()}")

        self._state = self._state.update(now_ms)
        
        new_state_name = self._state.get_graphics().sprites_folder.parent.name
        # print(f"[{self.piece_id}] After update: New state is {new_state_name}, Graphics loop: {self._state.get_graphics().loop}, Graphics finished: {self._state.get_graphics().is_finished()}")
        if prev_state_name != new_state_name:
            print(f"[{self.piece_id}] {prev_state_name} -> {new_state_name}")


    def draw_on_board(self, board: Board, now_ms: int):
        # self.update(now_ms)

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
            print(f"Warning: Piece drawing for {self.piece_id} at ({board_x_pix}, {board_y_pix}) exceeds board dimensions.")

        piece_img_obj.draw_on(other_img=board.img, x=draw_x, y=draw_y)

        if not self._state.can_transition(now_ms):
            cooldown_img = piece_img_obj.clone()
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

    def is_vulnerable(self) -> bool:
    # דוגמה: אם הפיזיקה מצביעה שהכלי לא בקפיצה, אז הוא פגיע
         return not self._state.get_graphics().sprites_folder.parent.name == "jump"


    def get_state(self) -> str:
        return self._state.get_state()