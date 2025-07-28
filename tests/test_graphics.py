import pytest
import tempfile
import shutil
import os
import pathlib
from unittest.mock import patch
import numpy as np

from implementation.graphics import Graphics
from implementation.board import Board
from implementation.command import Command
from implementation.mock_img import MockImg


@pytest.fixture(autouse=True)
def reset_mock_img_state():
    MockImg.reset()
    yield


@pytest.fixture
def dummy_board():
    mock_board_img = MockImg() 
    return Board(
        cell_H_pix=50,
        cell_W_pix=50,
        cell_H_m=1.0,
        cell_W_m=1.0,
        W_cells=8,
        H_cells=8,
        img=mock_board_img
    )


@pytest.fixture
def temp_sprites_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = pathlib.Path(tmpdir) / "test_sprites"
        folder_path.mkdir()

        (folder_path / "0000.png").touch()
        (folder_path / "0001.png").touch()
        (folder_path / "0002.png").touch() # 3 sprites, indices 0, 1, 2

        yield folder_path



## Graphics Tests

def test_graphics_initialization_and_sprite_loading(temp_sprites_folder, dummy_board):
    with patch('implementation.graphics.Img', new=MockImg):
        sprites_folder = temp_sprites_folder
        board = dummy_board
        loop = True
        fps = 10.0

        graphics = Graphics(
            sprites_folder=sprites_folder,
            board=board,
            loop=loop,
            fps=fps
        )

        assert graphics.sprites_folder == sprites_folder
        assert graphics.board == board
        assert graphics.loop is loop
        assert graphics.fps == fps
        assert graphics.cur_index == 0
        assert graphics.last_frame_time is None
        assert graphics.total_frames == 3 
        assert not graphics.animation_finished
        assert len(graphics.sprites) == 3
        
        assert len(MockImg.get_read_calls()) == 3
        assert all(isinstance(s, MockImg) for s in graphics.sprites)


def test_graphics_copy_method(temp_sprites_folder, dummy_board):
    with patch('implementation.graphics.Img', new=MockImg):
        original_graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=True,
            fps=5.0
        )
        original_graphics.cur_index = 1
        original_graphics.last_frame_time = 500
        original_graphics.animation_finished = True

        copied_graphics = original_graphics.copy()

        assert copied_graphics is not original_graphics
        assert copied_graphics.sprites_folder == original_graphics.sprites_folder
        assert copied_graphics.board is not original_graphics.board
        assert copied_graphics.loop == original_graphics.loop
        assert copied_graphics.fps == original_graphics.fps
        assert copied_graphics.cur_index == original_graphics.cur_index
        assert copied_graphics.last_frame_time == original_graphics.last_frame_time
        assert copied_graphics.total_frames == original_graphics.total_frames
        assert copied_graphics.animation_finished == original_graphics.animation_finished
        assert len(copied_graphics.sprites) == len(original_graphics.sprites)
        
        assert copied_graphics.sprites[0] is not original_graphics.sprites[0]
        assert all(isinstance(s, MockImg) for s in copied_graphics.sprites)
        assert all(isinstance(s, MockImg) for s in original_graphics.sprites)


def test_graphics_reset_method(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        
        graphics.cur_index = 2
        graphics.last_frame_time = 1000
        graphics.animation_finished = True

        reset_command_timestamp = 2000
        cmd_for_reset = Command(
            timestamp=reset_command_timestamp,
            piece_id="test_piece",
            type="RESET",
            params=[]
        )
        
        graphics.reset(cmd_for_reset)

        assert graphics.cur_index == 0
        assert graphics.last_frame_time == reset_command_timestamp
        assert graphics.animation_finished is False


def test_graphics_update_advances_frame_when_time_elapses(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0

        result = graphics.update(now_ms=1000)

        assert result is None
        assert graphics.cur_index == 1
        assert graphics.last_frame_time == 1000


def test_graphics_update_loops_when_loop_is_true(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=True,
            fps=1.0
        )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0

        graphics.update(now_ms=3000) 

        assert graphics.cur_index == 0
        assert graphics.last_frame_time == 3000
        assert not graphics.animation_finished


def test_graphics_update_finishes_animation_when_loop_is_false(dummy_board, temp_sprites_folder):
    """Tests that update finishes animation when loop is disabled."""
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder, # 3 files (0, 1, 2)
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0

        # Advance to index 1
        graphics.update(now_ms=1000)
        assert graphics.cur_index == 1
        assert not graphics.is_finished()

        # Advance to index 2 (last frame)
        graphics.update(now_ms=2000)
        assert graphics.cur_index == 2
        assert not graphics.is_finished() # Still not finished, as we are on the last frame

        # Advance beyond the last frame (to index 3 if it existed).
        # This update should cause cur_index to be capped at 2, and animation_finished to become True.
        graphics.update(now_ms=3000) 
        
        assert graphics.cur_index == 2 # Should be capped at the last valid index
        assert graphics.animation_finished is True
        assert graphics.is_finished() # This should now pass
        # Additionally, if you call update again after it's finished and not looping,
        # it should return None and not change state.
        assert graphics.update(now_ms=4000) is None


def test_graphics_get_img_returns_current_sprite(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=True,
            fps=10.0
        )
        
        graphics.cur_index = 1

        current_img = graphics.get_img()

        assert isinstance(current_img, MockImg)
        assert current_img is graphics.sprites[1]


def test_graphics_initialization_with_empty_sprites_folder_raises_error(dummy_board):
    with patch('implementation.graphics.Img', new=MockImg):
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_folder_path = pathlib.Path(tmpdir) / "empty_sprites"
            empty_folder_path.mkdir()

            with pytest.raises(ValueError, match="No sprites found in:"):
                Graphics(
                    sprites_folder=empty_folder_path,
                    board=dummy_board,
                    loop=True,
                    fps=10.0
                )


def test_graphics_update_no_time_elapsed_no_frame_advance(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=True,
            fps=1.0
        )
        
        graphics.last_frame_time = 1000
        graphics.cur_index = 0

        result = graphics.update(now_ms=1050)

        assert result is None
        assert graphics.cur_index == 0
        assert graphics.last_frame_time == 1000


def test_graphics_update_animation_finished_no_loop_returns_none(dummy_board, temp_sprites_folder):
    """Tests that update returns None when animation is finished and not looping."""
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0
        graphics.animation_finished = True # Manually set to finished for this test

        result = graphics.update(now_ms=100)

        assert result is None
        assert graphics.cur_index == 0
        assert graphics.last_frame_time == 0


def test_graphics_is_finished_method_returns_true_when_finished_and_no_loop(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        graphics.animation_finished = True

        assert graphics.is_finished() is True


def test_graphics_is_finished_method_returns_false_when_looping(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=True,
            fps=1.0
        )
        graphics.animation_finished = True

        assert graphics.is_finished() is False


def test_graphics_is_finished_method_returns_false_when_not_finished_and_no_loop(dummy_board, temp_sprites_folder):
    with patch('implementation.graphics.Img', new=MockImg):
        graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board,
            loop=False,
            fps=1.0
        )
        graphics.animation_finished = False

        assert graphics.is_finished() is False