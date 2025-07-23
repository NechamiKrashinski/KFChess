# import pytest
# import tempfile
# import shutil
# import os
# import json
# import numpy as np
# from pathlib import Path
# from unittest.mock import patch

# from implementation.board import Board
# from implementation.piece_factory import PieceFactory
# from implementation.piece import Piece
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

# @pytest.fixture
# def temp_piece_dir():
#     base_dir = Path(tempfile.mkdtemp())
#     pb_dir = base_dir / "PB"
#     states_dir = pb_dir / "states" / "idle" / "sprites"
#     states_dir.mkdir(parents=True)

#     dummy_img_path = states_dir / "0000.png"
#     dummy_img_path.write_bytes(np.zeros((10, 10, 4), dtype=np.uint8).tobytes())

#     moves_txt = pb_dir / "moves.txt"
#     moves_txt.write_text("0,0:idle\n")

#     config = {
#         "id": "PB",
#         "moves": "moves.txt",
#         "transitions": {
#             "idle": {"click": "idle"}
#         },
#         "physics": {"speed": 1.0}
#     }
#     with open(pb_dir / "config.json", 'w') as f:
#         json.dump(config, f)

#     yield base_dir
#     shutil.rmtree(base_dir)

# def test_create_piece_success(temp_piece_dir, dummy_board):
#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with patch("cv2.imread", return_value=np.ones((10, 10, 4), dtype=np.uint8)):
#         piece = factory.create_piece("PB", (1, 2))

#     assert isinstance(piece, Piece)
#     assert piece._state is not None
#     assert piece._state.get_graphics() is not None
#     assert piece._state.get_physics() is not None

# def test_create_piece_invalid_type(temp_piece_dir, dummy_board):
#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with pytest.raises(ValueError, match="Unknown piece type"):
#         factory.create_piece("INVALID", (0, 0))

# def test_config_missing_moves(temp_piece_dir, dummy_board):
#     cfg_path = temp_piece_dir / "PB" / "config.json"
#     with open(cfg_path) as f:
#         cfg = json.load(f)
#     del cfg["moves"]
#     with open(cfg_path, "w") as f:
#         json.dump(cfg, f)

#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with pytest.raises(KeyError, match="Missing 'moves' in config"):
#         factory.create_piece("PB", (0, 0))

# def test_missing_config_file(dummy_board):
#     base_dir = Path(tempfile.mkdtemp())
#     (base_dir / "PB").mkdir()
#     factory = PieceFactory(dummy_board, base_dir)
#     assert "PB" not in factory.templates
#     shutil.rmtree(base_dir)

# def test_no_sprites_in_state(temp_piece_dir, dummy_board):
#     sprite_dir = temp_piece_dir / "PB" / "states" / "idle" / "sprites"
#     for f in sprite_dir.iterdir():
#         f.unlink()

#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with pytest.raises(ValueError, match="No valid states found for piece PB"):
#         factory.create_piece("PB", (0, 0))

# def test_missing_sprite_image_file(temp_piece_dir, dummy_board):
#     sprite_file = temp_piece_dir / "PB" / "states" / "idle" / "sprites" / "0000.png"
#     sprite_file.unlink()

#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with pytest.raises(ValueError, match="No valid states found for piece PB"):
#         factory.create_piece("PB", (0, 0))

# def test_multiple_transitions_defined(temp_piece_dir, dummy_board):
#     cfg_path = temp_piece_dir / "PB" / "config.json"
#     with open(cfg_path) as f:
#         cfg = json.load(f)
#     cfg["transitions"] = {
#         "idle": {"click": "idle", "hover": "idle"},
#         "other": {"press": "idle"}
#     }
#     with open(cfg_path, "w") as f:
#         json.dump(cfg, f)

#     factory = PieceFactory(dummy_board, temp_piece_dir)
#     with patch("cv2.imread", return_value=np.ones((10, 10, 4), dtype=np.uint8)):
#         piece = factory.create_piece("PB", (0, 0))

#     assert piece._state.get_graphics() is not None