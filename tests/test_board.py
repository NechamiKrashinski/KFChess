import numpy as np
import pytest
from implementation.img import Img
from implementation.board import Board

@pytest.fixture
def sample_board():
    img = Img()
    img.img = np.zeros((100, 100, 4), dtype=np.uint8)
    board = Board(
        cell_H_pix=10,
        cell_W_pix=10,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=10,
        H_cells=10,
        img=img
    )
    return board

# 🧪 שכפול אובייקט – clone
def test_clone_independence(sample_board):
    clone = sample_board.clone()
    assert clone is not sample_board
    assert clone.img is not sample_board.img
    assert np.array_equal(clone.img.img, sample_board.img.img)

    # שינוי בקלון לא משפיע על המקור
    clone.img.img[0, 0, 0] = 255
    assert clone.img.img[0, 0, 0] != sample_board.img.img[0, 0, 0]

# 🧪 בדיקת ערכים ראשיים
def test_board_basic_attributes(sample_board):
    assert sample_board.cell_H_pix == 10
    assert sample_board.cell_W_pix == 10
    assert sample_board.cell_H_m == 1
    assert sample_board.cell_W_m == 1
    assert sample_board.W_cells == 10
    assert sample_board.H_cells == 10

# 🧪 בדיקת מימדים תואמים של תמונה ללוח
def test_image_dimensions_match_board(sample_board):
    expected_height = sample_board.cell_H_pix * sample_board.H_cells
    expected_width = sample_board.cell_W_pix * sample_board.W_cells
    img_height, img_width, _ = sample_board.img.img.shape
    assert img_height == expected_height
    assert img_width == expected_width

# 🧪 שינוי גודל בלוח לא משפיע על התמונה
def test_mutate_dimensions_only(sample_board):
    sample_board.cell_H_pix = 20
    sample_board.cell_W_pix = 20
    assert sample_board.cell_H_pix == 20
    assert sample_board.img.img.shape == (100, 100, 4)

# 🧪 בדיקה שה־clone שומר על אותו גודל פיזי ולוגי
def test_clone_has_same_dimensions(sample_board):
    clone = sample_board.clone()
    assert clone.cell_H_pix == sample_board.cell_H_pix
    assert clone.cell_W_pix == sample_board.cell_W_pix
    assert clone.cell_H_m == sample_board.cell_H_m
    assert clone.cell_W_m == sample_board.cell_W_m
    assert clone.W_cells == sample_board.W_cells
    assert clone.H_cells == sample_board.H_cells
    assert clone.img.img.shape == sample_board.img.img.shape
