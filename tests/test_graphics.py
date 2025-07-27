import pytest
import tempfile
import shutil
import os
import pathlib
from unittest.mock import patch
import numpy as np

# ייבוא המחלקות האמיתיות
from implementation.graphics import Graphics
from implementation.board import Board
from implementation.command import Command
from implementation.img import Img # נשאר לייבא את Img כי Graphics משתמשת בו
from implementation.mock_img import MockImg # ייבוא MockImg הקיים שלך

# Fixture for a dummy Board instance (using the real Board)
@pytest.fixture
def dummy_board():
    # יוצרים מופע אמיתי של Board
    return Board(
        cell_H_pix=50,
        cell_W_pix=50,
        cell_H_m=1.0, # ערכים סבירים
        cell_W_m=1.0, # ערכים סבירים
        W_cells=8,
        H_cells=8,
        img=MockImg() # Board גם מקבל Img, אז נשתמש ב-MockImg גם כאן
    )

# Fixture for a temporary sprites folder with dummy images
@pytest.fixture
def temp_sprites_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = pathlib.Path(tmpdir) / "test_sprites"
        folder_path.mkdir()

        # Create dummy PNG files
        # חשוב: חייבים שיהיו קבצים פיזיים כדי ש-glob ימצא אותם
        (folder_path / "0000.png").touch()
        (folder_path / "0001.png").touch()
        (folder_path / "0002.png").touch()

        yield folder_path

### --- SANITY TESTS ---

def test_graphics_initialization_and_sprite_loading(temp_sprites_folder, dummy_board):
    # Arrange
    sprites_folder = temp_sprites_folder
    board = dummy_board # משתמשים במופע Board האמיתי מה-fixture
    loop = True
    fps = 10.0

    # Act
    # נדמה את Img.read כדי שיחזיר MockImg, כפי שביקשת.
    # זה מונע קריאה אמיתית של קבצי תמונה.
    with patch('implementation.img.Img.read', return_value=MockImg()) as mock_img_read_method:
        graphics = Graphics(
            sprites_folder=sprites_folder,
            board=board,
            loop=loop,
            fps=fps
        )

        # Assert
        assert graphics.sprites_folder == sprites_folder
        assert graphics.board == board # בודקים שזה אותו מופע Board
        assert graphics.loop is loop
        assert graphics.fps == fps
        assert graphics.cur_index == 0
        assert graphics.last_frame_time is None
        assert graphics.total_frames == 3 # Should have loaded 3 dummy sprites
        assert not graphics.animation_finished
        assert len(graphics.sprites) == 3
        # ודא ש-Img.read נקרא עבור כל ספריט
        assert mock_img_read_method.call_count == 3
        # ודא שכל הספריטים הם מופעים של MockImg
        assert all(isinstance(s, MockImg) for s in graphics.sprites)


def test_graphics_copy_method(temp_sprites_folder, dummy_board):
    # Arrange
    # נדמה את Img.read עבור original_graphics
    with patch('implementation.img.Img.read', return_value=MockImg()):
        original_graphics = Graphics(
            sprites_folder=temp_sprites_folder,
            board=dummy_board, # משתמשים ב-Board האמיתי
            loop=True,
            fps=5.0
        )
        original_graphics.cur_index = 1
        original_graphics.last_frame_time = 500
        original_graphics.animation_finished = True

        # Act
        copied_graphics = original_graphics.copy()

        # Assert
        assert copied_graphics is not original_graphics # צריך להיות מופע חדש
        assert copied_graphics.sprites_folder == original_graphics.sprites_folder
        # בודקים ש-Board בתוך copied_graphics הוא עותק (או מופע חדש אם Board.clone() יוצר כזה)
        assert copied_graphics.board is not original_graphics.board
        # אולי נצטרך גם לוודא ש board.clone() נקרא אם יש לכם כזו מתודה ב-Board
        # אם אין clone() ב-Board, צריך לשנות את Graphics.copy() שלא תקרא לזה
        # אם יש, הייתי שוקל למקק רק את clone() ולא את כל ה-Board אם הוא מורכב.
        
        assert copied_graphics.loop == original_graphics.loop
        assert copied_graphics.fps == original_graphics.fps
        assert copied_graphics.cur_index == original_graphics.cur_index
        assert copied_graphics.last_frame_time == original_graphics.last_frame_time
        assert copied_graphics.total_frames == original_graphics.total_frames
        assert copied_graphics.animation_finished == original_graphics.animation_finished
        assert len(copied_graphics.sprites) == len(original_graphics.sprites)
        # ודא שהספריטים הם עותקים עמוקים, לא רק הפניות
        assert copied_graphics.sprites[0] is not original_graphics.sprites[0]
        assert isinstance(copied_graphics.sprites[0], MockImg)


def test_graphics_reset_method(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        # הקמת גרפיקה עם Board אמיתי
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_sprites_reset"
            folder_path.mkdir()
            (folder_path / "0000.png").touch() # לפחות ספריט אחד

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False,
                fps=1.0
            )
        
        # הדמיית התקדמות כלשהי באנימציה
        graphics.cur_index = 2
        graphics.last_frame_time = 1000
        graphics.animation_finished = True

        reset_command_timestamp = 2000
        # יצירת מופע Command אמיתי
        cmd_for_reset = Command(
            timestamp=reset_command_timestamp,
            piece_id="test_piece",
            type="RESET",
            params=[]
        )
    
    # Act
    graphics.reset(cmd_for_reset)

    # Assert
    assert graphics.cur_index == 0
    assert graphics.last_frame_time == reset_command_timestamp
    assert graphics.animation_finished is False


def test_graphics_update_advances_frame_when_time_elapses(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_sprites_update"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()
            (folder_path / "0001.png").touch()
            (folder_path / "0002.png").touch() # 3 sprites for 0, 1, 2 indices

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False,
                fps=1.0 # 1 frame per second
            )
        
        # מצב התחלתי
        graphics.last_frame_time = 0 # זמן התחלה
        graphics.cur_index = 0

        # Act - הדמיית מעבר של שנייה אחת
        result = graphics.update(now_ms=1000) # 1000 ms = 1 second

        # Assert
        assert result is None # update לא מחזיר פקודה
        assert graphics.cur_index == 1 # אמור להתקדם מ-0 ל-1
        assert graphics.last_frame_time == 1000 # last_frame_time אמור להתעדכן


def test_graphics_update_loops_when_loop_is_true(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_sprites_loop"
            folder_path.mkdir()
            # 2 sprites
            (folder_path / "0000.png").touch()
            (folder_path / "0001.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=True, # הגדר ל-True
                fps=1.0 # 1 frame per second
            )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0 # התחל באינדקס 0

        # Act - הדמיית מעבר של 3 שניות (אמור לעבור דרך 0, 1, ולחזור ל-0)
        graphics.update(now_ms=3000) # 3 שניות, 3 פריימים התקדמו

        # Assert
        # total_frames = 2. cur_index should be (0 + 3) % 2 = 1
        assert graphics.cur_index == 1
        assert graphics.last_frame_time == 3000
        assert not graphics.animation_finished # לא אמור להיות finished אם יש לולאה


def test_graphics_update_finishes_animation_when_loop_is_false(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_sprites_no_loop"
            folder_path.mkdir()
            # 2 sprites (אינדקסים 0, 1)
            (folder_path / "0000.png").touch()
            (folder_path / "0001.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False, # הגדר ל-False
                fps=1.0 # 1 frame per second
            )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0

        # Act 1: התקדמות מספיקה כדי להגיע לסוף (אינדקס 1)
        graphics.update(now_ms=1000) # מתקדם פריים אחד, cur_index הופך ל-1
        assert graphics.cur_index == 1
        assert not graphics.is_finished() # עדיין לא אמור להיות finished

        # Act 2: התקדמות מעבר לסוף (אינדקס 1 -> מנסה ללכת ל-2)
        # זה אמור לגרום ל-animation_finished להפוך ל-True
        graphics.update(now_ms=2000)

        # Assert
        assert graphics.cur_index == 1 # אמור להיצמד לאינדקס האחרון
        assert graphics.animation_finished is True # אנימציה אמורה להיות מסומנת כגמורה
        assert graphics.is_finished() # is_finished אמור להחזיר True


def test_graphics_get_img_returns_current_sprite(dummy_board):
    # Arrange
    # נדמה את Img.read כך שיחזיר מופעים שונים של MockImg
    with patch('implementation.img.Img.read', side_effect=[MockImg(), MockImg(), MockImg()]):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_get_img"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()
            (folder_path / "0001.png").touch()
            (folder_path / "0002.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=True,
                fps=10.0
            )
        
        # הגדר ידנית את האינדקס הנוכחי
        graphics.cur_index = 1

        # Act
        current_img = graphics.get_img()

        # Assert
        assert isinstance(current_img, MockImg)
        assert current_img is graphics.sprites[1] # ודא שזה אותו מופע בזיכרון


### --- EDGE CASES ---

def test_graphics_initialization_with_empty_sprites_folder_raises_error(dummy_board):
    # Arrange
    # יצירת תיקייה זמנית ריקה
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_folder_path = pathlib.Path(tmpdir) / "empty_sprites"
        empty_folder_path.mkdir()

        # Act & Assert
        with pytest.raises(ValueError, match="No sprites found in:"):
            Graphics(
                sprites_folder=empty_folder_path,
                board=dummy_board,
                loop=True,
                fps=10.0
            )


def test_graphics_update_no_time_elapsed_no_frame_advance(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_no_advance"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()
            (folder_path / "0001.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=True,
                fps=1.0
            )
        
        graphics.last_frame_time = 1000 # הדמיית עדכון אחרון ב-1000ms
        graphics.cur_index = 0

        # Act
        result = graphics.update(now_ms=1050) # רק 50ms עברו, לא מספיק לפריים אחד ב-1 FPS

        # Assert
        assert result is None
        assert graphics.cur_index == 0 # לא אמור להתקדם
        assert graphics.last_frame_time == 1000 # לא אמור לעדכן את last_frame_time


def test_graphics_update_animation_finished_no_loop_returns_none(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_finished"
            folder_path.mkdir()
            (folder_path / "0000.png").touch() # ספריט בודד, לכן "נגמר" מיד אם loop הוא false

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False,
                fps=1.0
            )
        
        graphics.last_frame_time = 0
        graphics.cur_index = 0
        graphics.animation_finished = True # קבע ידנית כ-finished

        # Act
        result = graphics.update(now_ms=100) # נסה לעדכן אנימציה שנגמרה

        # Assert
        assert result is None # אמור להחזיר None מיד
        assert graphics.cur_index == 0 # לא אמור להשתנות
        assert graphics.last_frame_time == 0 # לא אמור להשתנות


def test_graphics_is_finished_method_returns_true_when_finished_and_no_loop(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_is_finished_true"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False, # בלי לולאה
                fps=1.0
            )
        graphics.animation_finished = True

        # Act & Assert
        assert graphics.is_finished() is True


def test_graphics_is_finished_method_returns_false_when_looping(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_is_finished_false_loop"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=True, # עם לולאה
                fps=1.0
            )
        graphics.animation_finished = True # גם אם true, אם יש לולאה זה לא "גמור"

        # Act & Assert
        assert graphics.is_finished() is False

def test_graphics_is_finished_method_returns_false_when_not_finished_and_no_loop(dummy_board):
    # Arrange
    with patch('implementation.img.Img.read', return_value=MockImg()):
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_path = pathlib.Path(tmpdir) / "test_is_finished_false_not_finished"
            folder_path.mkdir()
            (folder_path / "0000.png").touch()

            graphics = Graphics(
                sprites_folder=folder_path,
                board=dummy_board,
                loop=False, # בלי לולאה
                fps=1.0
            )
        graphics.animation_finished = False # לא גמור עדיין

        # Act & Assert
        assert graphics.is_finished() is False