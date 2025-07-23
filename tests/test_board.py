import pytest
import numpy as np
from dataclasses import dataclass
from pathlib import Path

# וודא שהייבוא נכון בהתאם למבנה התיקיות שלך
# אם Board נמצא באותה תיקייה כמו test_board.py
from implementation.board import Board
# אם MockImg נמצא באותה תיקייה כמו test_board.py
from implementation.mock_img import MockImg


# Fixture לניקוי ה-Mock.traj ו-Mock.txt_traj לפני כל בדיקה
@pytest.fixture(autouse=True)
def reset_mock_img_data():
    """מאתחל את נתוני התיעוד ב-MockImg לפני כל בדיקה."""
    MockImg.reset()
    yield


# --- בדיקות למתודת clone ---

def test_clone_creates_new_board_instance():
    """
    Arrange: יצירת אובייקט Board עם MockImg.
    Act: שיבוט אובייקט ה-Board.
    Assert: ודא שהאובייקט החדש הוא מופע שונה של Board.
    """
    # Arrange
    original_img_mock = MockImg()
    original_img_mock.read(Path("dummy_path.png")) # לדמות טעינה של תמונה
    original_board = Board(
        cell_H_pix=10, cell_W_pix=10,
        cell_H_m=1, cell_W_m=1,
        W_cells=5, H_cells=5,
        img=original_img_mock
    )

    # Act
    cloned_board = original_board.clone()

    # Assert
    assert isinstance(cloned_board, Board)
    assert cloned_board is not original_board # ודא שזה אובייקט שונה בזיכרון


def test_clone_performs_deep_copy_of_img():
    """
    Arrange: יצירת אובייקט Board עם MockImg, שיבוט שלו.
    Act: שינוי מאפיין ב-MockImg של האובייקט המקורי.
    Assert: ודא שה-MockImg באובייקט המשובט לא הושפע (כלומר, בוצעה העתקה עמוקה).
    """
    # Arrange
    original_img_mock = MockImg()
    original_img_mock.read(Path("dummy_path.png")) # לדמות טעינה של תמונה
    original_img_mock.img = np.full((50, 50, 4), 255, dtype=np.uint8) # תמונה לבנה
    
    original_board = Board(
        cell_H_pix=10, cell_W_pix=10,
        cell_H_m=1, cell_W_m=1,
        W_cells=5, H_cells=5,
        img=original_img_mock
    )

    # Act
    cloned_board = original_board.clone()
    
    # שנה את התמונה באובייקט המקורי
    original_board.img.img[0, 0] = [0, 0, 0, 255] # שנה פיקסל אחד לשחור

    # Assert
    # ודא שאובייקט ה-Img בלוח המשובט הוא גם MockImg נפרד
    assert isinstance(cloned_board.img, MockImg)
    assert cloned_board.img is not original_board.img
    
    # ב-MockImg, העתקה עמוקה משמעותה שצורת ה-img.img תהיה זהה,
    # אך מכיוון שהוא 'mock', שינויים בפועל על המערך הפנימי שלו לא תמיד משתקפים.
    # הדרך הטובה ביותר לבדוק העתקה עמוקה של ה-MockImg היא לבדוק את ה-id של מערך ה-numpy הפנימי
    # או לוודא שקריאה ל-clone של Img התרחשה.
    # מכיוון ש-MockImg.clone() יוצר מופע חדש עם מערך חדש (גם אם באותו גודל),
    # אנו בודקים שאכן יש מופעים שונים של ה-img.
    assert id(cloned_board.img.img) != id(original_board.img.img)
    assert np.array_equal(cloned_board.img.img[0,0], [255, 255, 255, 255]) # ודא שהפיקסל לא השתנה בשיבוט
    assert np.array_equal(original_board.img.img[0,0], [0, 0, 0, 255]) # ודא שהפיקסל השתנה במקור


def test_clone_copies_all_scalar_attributes_correctly():
    """
    Arrange: יצירת אובייקט Board עם ערכים שונים למאפיינים.
    Act: שיבוט אובייקט ה-Board.
    Assert: ודא שכל המאפיינים הסקלריים הועתקו כהלכה.
    """
    # Arrange
    original_img_mock = MockImg()
    original_img_mock.read(Path("dummy_path.png"))
    original_board = Board(
        cell_H_pix=20,
        cell_W_pix=30,
        cell_H_m=2,
        cell_W_m=3,
        W_cells=10,
        H_cells=8,
        img=original_img_mock
    )

    # Act
    cloned_board = original_board.clone()

    # Assert
    assert cloned_board.cell_H_pix == 20
    assert cloned_board.cell_W_pix == 30
    assert cloned_board.cell_H_m == 2
    assert cloned_board.cell_W_m == 3
    assert cloned_board.W_cells == 10
    assert cloned_board.H_cells == 8