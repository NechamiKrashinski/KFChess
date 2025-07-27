from implementation.command import Command


class KeyboardInputHandler:
    def __init__(self, game: 'Game'):
        self.game = game

    def handle_keyboard_input(self, key: int) -> bool:
        current_col, current_row = self.game.keyboard_cursor_cell
        moved = False

        if key == ord('w') and current_row > 0:
            self.game.keyboard_cursor_cell = (current_col, current_row - 1)
            moved = True
        elif key == ord('s') and current_row < self.game.board.H_cells - 1:
            self.game.keyboard_cursor_cell = (current_col, current_row + 1)
            moved = True
        elif key == ord('a') and current_col > 0:
            self.game.keyboard_cursor_cell = (current_col - 1, current_row)
            moved = True
        elif key == ord('d') and current_col < self.game.board.W_cells - 1:
            self.game.keyboard_cursor_cell = (current_col + 1, current_row)
            moved = True
        elif key == 13:  # Enter key
            self._handle_keyboard_action(self.game.keyboard_cursor_cell)
            moved = True

        if moved:
            print(f"Keyboard cursor (or action) at: {self.game.keyboard_cursor_cell}")

        return key != 27  # ESC key

    def _handle_keyboard_action(self, cell_coords: Tuple[int, int]):
        clicked_piece_id = None
        for pid, piece in self.game.pieces.items():
            if piece.get_physics().get_cell() == cell_coords:
                clicked_piece_id = pid
                break

        if self.game.keyboard_selected_piece_id is None:
            if clicked_piece_id:
                if clicked_piece_id[1] == self.game.keyboard_player_color:
                    self.game.keyboard_selected_piece_id = clicked_piece_id
                    self.game.keyboard_selected_piece_original_cell = cell_coords
                else:
                    print(f"Keyboard cannot select opponent's piece: {clicked_piece_id}")
            else:
                print(f"No piece at {cell_coords} for keyboard selection.")
        else:
            target_cell = cell_coords
            piece_to_move = self.game.pieces[self.game.keyboard_selected_piece_id]
            moves = piece_to_move.get_moves(list(self.game.pieces.values()))

            if target_cell == self.game.keyboard_selected_piece_original_cell:
                cmd = Command(
                    timestamp=self.game.game_time_ms(),
                    piece_id=self.game.keyboard_selected_piece_id,
                    type="Jump",
                    params=list(target_cell)
                )
                self.game.user_input_queue.put(cmd)
            else:
                if target_cell in moves:
                    cmd = Command(
                        timestamp=self.game.game_time_ms(),
                        piece_id=self.game.keyboard_selected_piece_id,
                        type="Move",
                        params=list(target_cell),
                        source_cell=self.game.keyboard_selected_piece_original_cell
                    )
                    self.game.user_input_queue.put(cmd)

            self.game.keyboard_selected_piece_id = None
            self.game.keyboard_selected_piece_original_cell = None
