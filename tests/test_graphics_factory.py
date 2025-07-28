# import pytest
# import tempfile
# import shutil
# import pathlib
# import numpy as np
# import cv2
# from unittest.mock import patch, MagicMock

# # Ensure MockImg is imported from where it's defined
# from implementation.graphics_factory import GraphicsFactory
# from implementation.graphics import Graphics
# from implementation.board import Board 
# from implementation.mock_img import MockImg # Make sure this path is correct

# @pytest.fixture
# def temp_sprite_dir():
#     with tempfile.TemporaryDirectory() as tmpdir:
#         root = pathlib.Path(tmpdir)

#         # Create dummy directories for pieces and states
#         for piece_id in ["PB", "QW"]:
#             for state in ["idle", "move"]:
#                 sprite_path = root / piece_id / "states" / state / "sprites"
#                 sprite_path.mkdir(parents=True, exist_ok=True)
#                 # Create actual dummy files for glob to find.
#                 # .touch() ensures the file exists for pathlib.Path.glob()
#                 for i in range(2):
#                     (sprite_path / f"{i}.png").touch() 

#         yield root


# @pytest.fixture
# def dummy_board():
#     class MockBoard:
#         def __init__(self):
#             self.cell_H_pix = 64
#             self.cell_W_pix = 64
        
#         def clone(self):
#             return MockBoard()
            
#     return MockBoard()


# @pytest.fixture(autouse=True)
# def mock_img_and_graphics_dependencies():
#     # Patch the Img class that 'implementation.graphics' imports
#     # This ensures that any 'Img()' call within Graphics.py becomes a MockImg()
#     # Also patch cv2.imwrite, though it might be less critical here.
#     with patch('implementation.graphics.Img', new=MockImg) as mock_img_class, \
#          patch('cv2.imwrite') as mock_imwrite:
        
#         # Ensure MockImg.read always sets a valid .img attribute and returns self.
#         # This is to satisfy Graphics._load_sprites's expectations.
#         original_mock_img_read = MockImg.read
#         def custom_read(self, path, target_size=None):
#             # Call the original mock read, which typically logs or performs basic setup
#             original_mock_img_read(self, path, target_size) 
#             # Crucially, ensure self.img is always a valid numpy array
#             effective_target_size = target_size if target_size is not None else (50, 50) 
#             # Using zeros to represent an image, ensure 4 channels (RGBA) as expected by tests
#             self.img = np.zeros((effective_target_size[1], effective_target_size[0], 4), dtype=np.uint8)
#             return self # Allows chaining like img.read(...).resize(...)

#         MockImg.read = custom_read
        
#         yield mock_img_class, mock_imwrite
        
#         # Clean up: restore original MockImg.read after tests are done
#         MockImg.read = original_mock_img_read


# def test_load_valid_graphics(temp_sprite_dir, dummy_board):
#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {"PB": True, "QW": True}

#     result = gf.load(temp_sprite_dir, cfg)

#     assert isinstance(result, dict)
#     assert "PB" in result
#     assert "QW" in result
#     assert "idle" in result["PB"]
#     assert "move" in result["PB"]

#     for piece_id in cfg:
#         for state in ["idle", "move"]:
#             g = result[piece_id][state]
#             assert isinstance(g, Graphics)
#             assert len(g.sprites) == 2
#             assert g.sprites[0].img.shape == (dummy_board.cell_H_pix, dummy_board.cell_W_pix, 4)


# def test_missing_states_folder(temp_sprite_dir, dummy_board):
#     shutil.rmtree(temp_sprite_dir / "QW" / "states")

#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {"PB": True, "QW": True}

#     with pytest.raises(FileNotFoundError, match=r"Missing states folder for QW: .*QW[/\\]states"):
#         gf.load(temp_sprite_dir, cfg)


# def test_empty_state_sprites(temp_sprite_dir, dummy_board):
#     sprite_dir = temp_sprite_dir / "PB" / "states" / "move" / "sprites"
#     for f in sprite_dir.iterdir():
#         f.unlink()

#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {"PB": True}

#     result = gf.load(temp_sprite_dir, cfg)

#     assert "PB" in result
#     assert "move" not in result["PB"]
#     assert "idle" in result["PB"]
#     assert isinstance(result["PB"]["idle"], Graphics)


# def test_no_valid_states_for_piece(temp_sprite_dir, dummy_board):
#     pb_dir = temp_sprite_dir / "PB"
#     if pb_dir.exists():
#         shutil.rmtree(pb_dir)
#     pb_dir.mkdir(parents=True, exist_ok=True)

#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {"PB": True, "QW": True}

#     result = gf.load(temp_sprite_dir, cfg)
    
#     assert "PB" not in result
#     assert "QW" in result


# def test_empty_config(temp_sprite_dir, dummy_board):
#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {}

#     result = gf.load(temp_sprite_dir, cfg)
#     assert result == {}


# def test_loop_and_fps_values_via_cfg(temp_sprite_dir, dummy_board):
#     gf = GraphicsFactory(board=dummy_board)
#     cfg = {
#         "PB": {
#             "graphics": {
#                 "frames_per_sec": 15,
#                 "is_loop": True
#             }
#         },
#         "QW": True
#     }
#     result = gf.load(temp_sprite_dir, cfg)

#     g_pb_idle = result["PB"]["idle"]
#     assert g_pb_idle.loop is True
#     assert g_pb_idle.fps == 15.0

#     g_qw_idle = result["QW"]["idle"]
#     assert g_qw_idle.loop is False 
#     assert g_qw_idle.fps == 6.0 

# def test_graphics_factory_initialization_with_board(dummy_board):
#     gf = GraphicsFactory(board=dummy_board)
#     assert gf.board is dummy_board

# def test_load_sprites_base_directory_not_found(dummy_board):
#     gf = GraphicsFactory(board=dummy_board)
#     non_existent_dir = pathlib.Path("./non_existent_sprites_folder_xyz_123") 

#     with pytest.raises(FileNotFoundError, match=r"Sprites base directory not found: .*non_existent_sprites_folder_xyz_123"):
#         gf.load(non_existent_dir, {"PB": True})