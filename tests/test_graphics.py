import pytest
import pathlib
import tempfile
import shutil
import cv2
import numpy as np

from implementation.img import Img
from implementation.graphics import Graphics
from implementation.command import Command
from implementation.board import Board

def _create_dummy_png(path, size=(64, 64), color=(0, 255, 0)):
    """Helper to create dummy image file"""
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img[:] = color
    cv2.imwrite(str(path), img)

@pytest.fixture
def sprite_folder():
    tmp = tempfile.mkdtemp()
    for i in range(5):
        _create_dummy_png(pathlib.Path(tmp) / f"sprite_{i}.png")
    yield pathlib.Path(tmp)
    shutil.rmtree(tmp)

@pytest.fixture
def dummy_board(tmp_path):
    # יצירת תמונת Dummy בשם test_img.png בתוך תיקיית הבדיקות (או בתיקיית זמנית)
    test_img_path = tmp_path / "test_img.png"

    if not test_img_path.exists():
        # יצירת תמונה ירוקה 512x512 פיקסלים
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        img[:] = (0, 255, 0)
        cv2.imwrite(str(test_img_path), img)

    return Board(
        cell_H_pix=64,
        cell_W_pix=64,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=Img().read(test_img_path, size=(512, 512), keep_aspect=False)
    )


def test_graphics_loads_sprites(sprite_folder, dummy_board):
    g = Graphics(sprite_folder, dummy_board)
    assert g.total_frames == 5
    assert len(g.sprites) == 5

def test_graphics_reset_sets_state(sprite_folder, dummy_board):
    g = Graphics(sprite_folder, dummy_board)
    cmd = Command(timestamp=1000, piece_id="p1", type="Move", params=[])
    g.reset(cmd)
    assert g.cur_index == 0
    assert g.last_frame_time == 1000

def test_graphics_update_looping(sprite_folder, dummy_board):
    g = Graphics(sprite_folder, dummy_board, loop=True, fps=5)
    cmd = Command(timestamp=0, piece_id="p1", type="Move", params=[])
    g.reset(cmd)

    g.update(1000)  # 1 שניה -> 5 פריימים
    assert g.cur_index == 0  # 5 % 5 == 0

    g.update(1200)  # 200ms יותר -> עוד פריים
    assert g.cur_index == 1

def test_graphics_update_no_loop(sprite_folder, dummy_board):
    g = Graphics(sprite_folder, dummy_board, loop=False, fps=2)
    cmd = Command(timestamp=0, piece_id="p1", type="Move", params=[])
    g.reset(cmd)

    g.update(3000)  # 3 שניות -> 6 פריימים → stop at last
    assert g.cur_index == 4  # capped at total_frames - 1

def test_get_img_returns_current_frame(sprite_folder, dummy_board):
    g = Graphics(sprite_folder, dummy_board)
    img0 = g.get_img()
    assert isinstance(img0, Img)

    g.cur_index = 2
    img2 = g.get_img()
    assert isinstance(img2, Img)
    assert img2 is g.sprites[2]
