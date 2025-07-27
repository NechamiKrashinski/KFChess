import cv2
from implementation.command import Command
from implementation.game import Game


class MouseInputHandler:
    def __init__(self, game: 'Game'):
        self.game = game

    def handle_mouse_input(self, event, x, y, flags):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        col = x // self.game.board.cell_W_pix
        row = y // self.game.board.cell_H_pix
        clicked_cell = (col, row)

        clicked_piece_id = None
        for pid, piece in self.game.pieces.items():
            if piece.get_physics().get_cell() == clicked_cell:
                clicked_piece_id = pid
                break

        if self.game.selected_piece_id is None:
            if clicked_piece_id:
                if clicked_piece_id[1] == self.game.mouse_player_color:
                    self.game.selected_piece_id = clicked_piece_id
                    self.game.selected_cell = clicked_cell
                else:
                    print(f"Mouse cannot select opponent's piece: {clicked_piece_id}")
            else:
                print(f"No piece at {clicked_cell} for mouse selection.")
        else:
            target_cell = clicked_cell
            piece = self.game.pieces[self.game.selected_piece_id]
            moves = piece.get_moves(list(self.game.pieces.values()))
            if target_cell == self.game.selected_cell:
                cmd = Command(
                    timestamp=self.game.game_time_ms(),
                    piece_id=self.game.selected_piece_id,
                    type="Jump",
                    params=list(target_cell)
                )
                self.game.user_input_queue.put(cmd)
            else:
                if target_cell in moves:
                    cmd = Command(
                        timestamp=self.game.game_time_ms(),
                        piece_id=self.game.selected_piece_id,
                        type="Move",
                        params=list(target_cell),
                        source_cell=self.game.selected_cell
                    )
                    self.game.user_input_queue.put(cmd)
                else:
                    print(f"Illegal move for {self.game.selected_piece_id} -> {target_cell}")

            self.game.selected_piece_id = None
            self.game.selected_cell = None
