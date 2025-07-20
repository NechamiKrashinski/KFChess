import numpy as np
import pytest
from implementation.img import Img
from implementation.Board import Board

@pytest.fixture
def sample_board():
    img = Img()
    img.img = np.zeros((100, 100, 4), dtype=np.uint8)
    board = Board(
        cell_H_pix=10,
        cell_W_pix=10,
        W_cells=10,
        H_cells=10,
        img=img
    )
    return board

def test_clone(sample_board):
    clone_board = sample_board.clone()

    # בדוק שזה אובייקט חדש
    assert clone_board is not sample_board

    # בדוק ערכים שווים
    assert clone_board.cell_H_pix == sample_board.cell_H_pix
    assert clone_board.cell_W_pix == sample_board.cell_W_pix
    assert clone_board.W_cells == sample_board.W_cells
    assert clone_board.H_cells == sample_board.H_cells

    # בדוק שהתמונה היא עותק חדש
    assert clone_board.img is not sample_board.img

     # בדוק שהתמונה שווה תוכן
    assert np.array_equal(clone_board.img.img, sample_board.img.img)

    # שינוי בקלון לא משפיע על המקור
    clone_board.img.img[0, 0, 0] = 255
    assert clone_board.img.img[0, 0, 0] != sample_board.img.img[0, 0, 0]
