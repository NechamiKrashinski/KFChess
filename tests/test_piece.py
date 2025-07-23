# import pytest
# import numpy as np
# from unittest.mock import MagicMock
# from implementation.piece import Piece
# from implementation.board import Board
# from implementation.mock_img import MockImg


# @pytest.fixture
# def dummy_board():
#     return Board(
#         cell_H_pix=100,
#         cell_W_pix=100,
#         cell_H_m=1,
#         cell_W_m=1,
#         W_cells=8,
#         H_cells=8,
#         img=MockImg()
#     )


# def test_draw_on_board_normal(dummy_board):
#     dummy_state = MagicMock()
#     dummy_graphics = MagicMock()
#     dummy_physics = MagicMock()

#     dummy_physics.get_pos.return_value = (2, 2)
#     dummy_graphics.get_img.return_value.img = np.ones((50, 50, 3), dtype=np.uint8)

#     dummy_state.get_graphics.return_value = dummy_graphics
#     dummy_state.get_physics.return_value = dummy_physics
#     dummy_state.can_transition.return_value = True
#     dummy_state.update.return_value = dummy_state

#     p = Piece("P1", dummy_state)
#     p.draw_on_board(dummy_board, now_ms=1000)


# def test_draw_on_board_with_cooldown(dummy_board):
#     dummy_state = MagicMock()
#     dummy_graphics = MagicMock()
#     dummy_physics = MagicMock()

#     dummy_physics.get_pos.return_value = (2, 2)
#     dummy_graphics.get_img.return_value.img = np.ones((50, 50, 3), dtype=np.uint8)

#     dummy_state.get_graphics.return_value = dummy_graphics
#     dummy_state.get_physics.return_value = dummy_physics
#     dummy_state.can_transition.return_value = False
#     dummy_state.update.return_value = dummy_state

#     p = Piece("P1", dummy_state)
#     p.draw_on_board(dummy_board, now_ms=1000)


# def test_draw_raises_if_out_of_bounds():
#     dummy_state = MagicMock()
#     dummy_graphics = MagicMock()
#     dummy_physics = MagicMock()

#     # קואורדינטות שממקמות את הפינה הימנית התחתונה מחוץ לתחומי הלוח
#     dummy_physics.get_pos.return_value = (7.5, 7.5)  # אחרון בתא 7 (מתוך 0-7)
#     dummy_graphics.get_img.return_value.img = np.ones((100, 100, 3), dtype=np.uint8)

#     dummy_state.get_graphics.return_value = dummy_graphics
#     dummy_state.get_physics.return_value = dummy_physics
#     dummy_state.update.return_value = dummy_state

#     board = Board(
#         cell_H_pix=100,
#         cell_W_pix=100,
#         cell_H_m=1,
#         cell_W_m=1,
#         W_cells=8,
#         H_cells=8,
#         img=MockImg()
#     )

#     p = Piece("P1", dummy_state)

#     with pytest.raises(ValueError, match="Image drawing exceeds board dimensions"):
#         p.draw_on_board(board, now_ms=1000)


# def test_draw_on_board_shape_mismatch(dummy_board):
#     dummy_state = MagicMock()
#     dummy_graphics = MagicMock()
#     dummy_physics = MagicMock()

#     dummy_physics.get_pos.return_value = (2, 2)
#     dummy_graphics.get_img.return_value.img = np.ones((100, 100, 3), dtype=np.uint8)

#     dummy_state.get_graphics.return_value = dummy_graphics
#     dummy_state.get_physics.return_value = dummy_physics
#     dummy_state.update.return_value = dummy_state

#     p = Piece("P1", dummy_state)

#     p.draw_on_board(dummy_board, now_ms=1000)
