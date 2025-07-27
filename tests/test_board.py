import pytest
import numpy as np
from pathlib import Path

from implementation.board import Board
from implementation.mock_img import MockImg

# Reset before each test to ensure isolation
@pytest.fixture(autouse=True)
def reset_mock_img_data():
    MockImg.reset()
    yield

# ---------- SANITY TESTS ----------

def test_clone_returns_new_board_with_same_attributes():
    # Arrange
    mock_img = MockImg().read(Path("dummy_path.png"))
    board = Board(
        cell_H_pix=10, cell_W_pix=20,
        cell_H_m=1, cell_W_m=2,
        W_cells=5, H_cells=6,
        img=mock_img
    )

    # Act
    cloned = board.clone()

    # Assert
    assert isinstance(cloned, Board)
    assert cloned is not board
    assert cloned.cell_H_pix == 10
    assert cloned.cell_W_pix == 20
    assert cloned.cell_H_m == 1
    assert cloned.cell_W_m == 2
    assert cloned.W_cells == 5
    assert cloned.H_cells == 6

def test_clone_deep_copies_image_object():
    # Arrange
    mock_img = MockImg().read(Path("dummy_path.png"), target_size=(30, 30))
    board = Board(10, 10, 1, 1, 3, 3, img=mock_img)

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.img is not board.img
    assert isinstance(cloned.img, MockImg)
    assert id(cloned.img.img) != id(board.img.img)
    assert np.array_equal(cloned.img.img, board.img.img)

def test_modifying_original_image_does_not_affect_clone():
    # Arrange
    mock_img = MockImg().read(Path("dummy_path.png"), target_size=(30, 30))
    mock_img.img[:, :] = [100, 100, 100, 255]
    board = Board(10, 10, 1, 1, 3, 3, img=mock_img)

    # Act
    cloned = board.clone()
    board.img.img[0, 0] = [0, 0, 0, 0]  # modify original

    # Assert
    assert not np.array_equal(cloned.img.img[0, 0], board.img.img[0, 0])
    assert np.array_equal(cloned.img.img[0, 0], [100, 100, 100, 255])

# ---------- EDGE CASES ----------

def test_clone_zero_dimension_board():
    # Arrange
    mock_img = MockImg().read(Path("dummy_path.png"), target_size=(1, 1))
    board = Board(
        cell_H_pix=0, cell_W_pix=0,
        cell_H_m=0, cell_W_m=0,
        W_cells=0, H_cells=0,
        img=mock_img
    )

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.W_cells == 0
    assert cloned.H_cells == 0
    assert cloned.cell_H_pix == 0
    assert cloned.cell_W_pix == 0
    assert cloned.cell_H_m == 0
    assert cloned.cell_W_m == 0
    assert cloned.img is not board.img

def test_clone_with_empty_image_raises_or_behaves_consistently():
    # Arrange
    mock_img = MockImg()
    mock_img.img = None  # simulate uninitialized image
    board = Board(10, 10, 1, 1, 3, 3, img=mock_img)

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.img is not board.img
    assert cloned.img.img is None

def test_clone_preserves_non_square_board():
    # Arrange
    mock_img = MockImg().read(Path("dummy_path.png"), target_size=(100, 40))
    board = Board(
        cell_H_pix=20,
        cell_W_pix=10,
        cell_H_m=2,
        cell_W_m=1,
        W_cells=10,
        H_cells=2,
        img=mock_img
    )

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.W_cells == 10
    assert cloned.H_cells == 2
    assert cloned.cell_H_pix == 20
    assert cloned.cell_W_pix == 10
    assert np.array_equal(cloned.img.img, board.img.img)
