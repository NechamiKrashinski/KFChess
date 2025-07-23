# tests/test_graphics.py
import pytest
import numpy as np
import pathlib
import time 
from typing import List, Dict, Tuple, Optional
from unittest.mock import patch 

# ייבוא המחלקות המקוריות הנבדקות
from implementation.board import Board
from implementation.img import Img
from implementation.graphics import Graphics
from implementation.command import Command 

# ייבוא מחלקות ה-Mock ישירות מ-conftest.py
# (אין צורך לייבא פיקסטורות, רק את המחלקות אם אתה משתמש בהן ישירות כמו כאן)
from .conftest import MockImg, MockBoard, MockCommand

# #--- הערה חשובה #---
# כל מחלקות ה-Mock (MockImg, MockBoard, MockCommand) וה-fixtures
# (כמו reset_mocks_fixture, mock_sprites_folder, mock_board, MockCommand_class)
# צריכים להיות מוגדרים אך ורק בקובץ conftest.py שלך.
# הם נגישים אוטומטית לבדיקות כאן מבלי צורך לייבא אותם מפורשות
# אלא אם אתה משתמש במחלקה עצמה כמו MockImg ב-patch.
# #---#---#---#---#---#---


## בדיקות ל-`__init__` ול-`_load_sprites` (שנקרא ב-init)
#---

# השתמש ב-patch כדי להחליף את implementation.graphics.Img ב-MockImg עבור בדיקות אלו
@patch('implementation.graphics.Img', new=MockImg)
def test_graphics_init_sanity_loads_sprites_correctly(mock_sprites_folder, mock_board):
    """
    Arrange: Create a MockBoard and a sprites folder with files.
    Act: Initialize a Graphics object.
    Assert: Verify sprites are loaded (non-empty list), total frames count is correct, and other attributes are initialized.
    """
    # Arrange
    # mock_board מתקבל כעת כארגומנט מה-fixture!
    
    # Act
    graphics_obj = Graphics(sprites_folder=mock_sprites_folder, board=mock_board)

    # Assert
    assert len(graphics_obj.sprites) == 3 # Number of dummy files created by mock_sprites_folder
    assert graphics_obj.total_frames == 3
    # ודא שאובייקטי Img שנטענו הם אכן מופעים של MockImg
    assert all(isinstance(sprite, MockImg) for sprite in graphics_obj.sprites)
    assert graphics_obj.cur_index == 0
    assert graphics_obj.last_frame_time is None
    assert graphics_obj.loop is True # Default
    assert graphics_obj.fps == 6.0 # Default


@patch('implementation.graphics.Img', new=MockImg)
def test_graphics_init_with_no_sprites_raises_valueerror(empty_mock_sprites_folder, mock_board):
    """
    Arrange: Create a MockBoard and an empty sprites folder.
    Act: Initialize a Graphics object.
    Assert: Verify a ValueError is raised when no sprites are found.
    """
    # Arrange
    # mock_board מתקבל כעת כארגומנט מה-fixture!

    # Act & Assert
    with pytest.raises(ValueError, match="No sprites found in:"):
        Graphics(sprites_folder=empty_mock_sprites_folder, board=mock_board)


@patch('implementation.graphics.Img', new=MockImg)
def test_graphics_init_with_custom_loop_and_fps(mock_sprites_folder, mock_board):
    """
    Arrange: Create a MockBoard, sprites folder, and custom loop/fps values.
    Act: Initialize a Graphics object.
    Assert: Verify loop and fps attributes are set correctly.
    """
    # Arrange
    custom_loop = False
    custom_fps = 15.0

    # Act
    graphics_obj = Graphics(
        sprites_folder=mock_sprites_folder,
        board=mock_board,
        loop=custom_loop,
        fps=custom_fps
    )

    # Assert
    assert graphics_obj.loop == custom_loop
    assert graphics_obj.fps == custom_fps


@patch('implementation.graphics.Img', new=MockImg)
def test_graphics_load_sprites_calls_img_read_with_target_size(mock_sprites_folder, mock_board):
    """
    Arrange: Create a MockBoard with specific dimensions and a sprites folder.
    Act: Initialize a Graphics object (which calls _load_sprites).
    Assert: Verify that MockImg.read would have been called with the correct target_size.
            (This is implicitly checked by MockImg's read setting its internal img shape).
    """
    # Arrange
    # MockBoard מאותחל עם מידות ברירת מחדל ב-fixture,
    # אבל אם אנחנו רוצים מידות ספציפיות, ניצור מופע חדש כאן.
    # אם תרצה שה-mock_board fixture יקבל פרמטרים, זה דורש שינוי ב-conftest.py
    # לדוגמה, fixture Factory
    custom_mock_board = mock_board # השתמש ב-fixture הקיים אם אין צורך בשינוי
    custom_mock_board.cell_W_pix = 100
    custom_mock_board.cell_H_pix = 75
    
    # Act
    graphics_obj = Graphics(sprites_folder=mock_sprites_folder, board=custom_mock_board)

    # Assert
    # Check that the MockImg objects indeed reflect the target_size passed to read
    read_calls = MockImg.get_read_calls()
    assert len(read_calls) == len(graphics_obj.sprites)
    for call_info in read_calls:
        assert call_info['target_size'] == (custom_mock_board.cell_W_pix, custom_mock_board.cell_H_pix)
    
    # בדיקה נוספת על האובייקטים שהוחזרו
    for sprite in graphics_obj.sprites:
        assert sprite.img.shape[1] == custom_mock_board.cell_W_pix # width
        assert sprite.img.shape[0] == custom_mock_board.cell_H_pix # height
        assert sprite.img.shape[2] == 4 # Ensure BGRA


## בדיקות למתודת `copy`
#---

@patch('implementation.graphics.Img', new=MockImg)
def test_graphics_copy_creates_deep_copy(tmp_path, mock_board):
    # Arrange
    sprites_folder = tmp_path / "copy_sprites"
    sprites_folder.mkdir()
    (sprites_folder / "s1.png").touch()
    (sprites_folder / "s2.png").touch()

    original_graphics = Graphics(sprites_folder=sprites_folder, board=mock_board)
    original_graphics.cur_index = 1
    original_graphics.last_frame_time = 1000

    # לפני העתקה, שנה את אחד מאובייקטי התמונה המדומה כדי לוודא שמוענק עותק עמוק
    # וודא שאובייקטי MockImg נוצרו ושהתמונה שלהם אינה None
    for sprite in original_graphics.sprites:
        if sprite.img is None:
            # קריאה ל-read כדי לאתחל את התמונה בתוך ה-MockImg
            # (בדרך כלל זה יקרה בתוך ה-Graphics.__init__ כשהוא טוען sprites)
            sprite.read(pathlib.Path("dummy.png"), target_size=(50, 50)) 
        sprite.img[0, 0] = [1, 2, 3, 4] # שנה לערך כלשהו שקל לזהות
    
    copied_graphics = original_graphics.copy()

    # Assertions...
    assert copied_graphics is not original_graphics
    assert copied_graphics.board is not original_graphics.board
    assert copied_graphics.board.cell_W_pix == original_graphics.board.cell_W_pix

    assert len(copied_graphics.sprites) == len(original_graphics.sprites)
    for i in range(len(copied_graphics.sprites)):
        assert copied_graphics.sprites[i] is not original_graphics.sprites[i]
        
        # וודא שהתמונה היא אכן עותק נפרד (ID שונה בזיכרון)
        assert id(copied_graphics.sprites[i].img) != id(original_graphics.sprites[i].img)
        
        # וודא שתוכן התמונה זהה מיד לאחר ההעתקה
        assert np.array_equal(copied_graphics.sprites[i].img, original_graphics.sprites[i].img)

        # כעת, בצע שינוי בעותק וודא שהמקור לא מושפע
        # שנה את הערך ב-copied_graphics
        copied_graphics.sprites[i].img[0, 0] = [255, 0, 0, 255] # ערך שונה מ-[1,2,3,4]

        # וודא שהשינוי בעותק לא השפיע על המקור
        assert not np.array_equal(copied_graphics.sprites[i].img, original_graphics.sprites[i].img)
        assert np.array_equal(original_graphics.sprites[i].img[0,0], [1, 2, 3, 4]) # וודא שהמקור נשאר כפי שהיה
        assert np.array_equal(copied_graphics.sprites[i].img[0,0], [255, 0, 0, 255]) # וודא שהעותק השתנה

    # וודא ששאר התכונות (לא רפרנסים) הועתקו כראוי
    assert copied_graphics.cur_index == original_graphics.cur_index
    assert copied_graphics.last_frame_time == original_graphics.last_frame_time
    assert copied_graphics.loop == original_graphics.loop
    assert copied_graphics.fps == original_graphics.fps

## בדיקות למתודת `reset`
#---

@patch('implementation.graphics.Img', new=MockImg)
def test_reset_sets_cur_index_to_zero_and_updates_timestamp(tmp_path, mock_board, MockCommand_class):
    """
    Arrange: Create a Graphics object in an arbitrary state.
    Act: Call reset with a new Command.
    Assert: Verify cur_index is reset to 0 and last_frame_time is updated.
    """
    # Arrange
    sprites_folder = tmp_path / "reset_sprites"
    sprites_folder.mkdir(exist_ok=True) 
    (sprites_folder / "s1.png").touch()

    graphics_obj = Graphics(sprites_folder=sprites_folder, board=mock_board)
    graphics_obj.cur_index = 5
    graphics_obj.last_frame_time = 100 # Some value

    # יצירת מופע MockCommand באמצעות ה-fixture של המחלקה
    cmd = MockCommand_class(timestamp=500, piece_id="p1", type="Move", params=[])

    # Act
    graphics_obj.reset(cmd)

    # Assert
    assert graphics_obj.cur_index == 0
    assert graphics_obj.last_frame_time == 500


## בדיקות למתודת `update`
#---

@pytest.mark.parametrize("loop, initial_index, total_frames, fps, elapsed_ms, expected_index, expected_timestamp", [
    # Sanity checks
    (True, 0, 3, 1.0, 1000, 1, 1000), # 1 sec, 1 fps, loop -> index 1
    (True, 0, 3, 2.0, 1000, 2, 1000), # 1 sec, 2 fps, loop -> index 2
    (True, 0, 3, 0.5, 1000, 0, 0), 
    (True, 0, 3, 1.0, 3000, 0, 3000), # 3 sec, 1 fps, loop -> index 3 % 3 = 0

    # No loop
    (False, 0, 3, 1.0, 1000, 1, 1000), # 1 sec, 1 fps, no loop -> index 1
    (False, 0, 3, 1.0, 3000, 2, 3000), # 3 sec, 1 fps, no loop -> index 2 (max index)
    (False, 0, 3, 1.0, 5000, 2, 5000), 
    # Edge cases
    (True, 0, 1, 1.0, 1000, 0, 1000), 
    (False, 0, 1, 1.0, 1000, 0, 1000),
    (True, 0, 3, 1.0, 0, 0, None), 
    (True, 0, 3, 1.0, 999, 0, None), 
    (True, 0, 3, 1.0, 1001, 1, 1001), 
])
@patch('implementation.graphics.Img', new=MockImg) # Apply patch here
def test_update_advances_frame_and_updates_time(
    mock_sprites_folder, mock_board, loop, initial_index, total_frames, fps, elapsed_ms, expected_index, expected_timestamp
):
    """
    Arrange: Initialize Graphics with specific parameters, set initial state.
    Act: Call update with current time.
    Assert: Verify cur_index is updated as expected and last_frame_time is updated.
    """
    # Arrange
    graphics_obj = Graphics(
        sprites_folder=mock_sprites_folder,
        board=mock_board,
        loop=loop,
        fps=fps
    )
    # Ensure total_frames matches test parameter (as _load_sprites might create based on dummy files)
    graphics_obj.total_frames = total_frames 
    # Ensure the sprites list has enough MockImg objects to avoid IndexError
    graphics_obj.sprites = [MockImg() for _ in range(total_frames)]


    graphics_obj.cur_index = initial_index # Set initial index for parameterized tests
    
    initial_time = 0 # Starting time for elapsed calculation
    graphics_obj.last_frame_time = initial_time # Manually set last_frame_time
    now_ms = initial_time + elapsed_ms

    # Act
    graphics_obj.update(now_ms)

    # Assert
    assert graphics_obj.cur_index == expected_index
    if expected_timestamp is not None:
        assert graphics_obj.last_frame_time == expected_timestamp
    else: # Case where time should not be updated
        assert graphics_obj.last_frame_time == initial_time


@patch('implementation.graphics.Img', new=MockImg) # Apply patch here
def test_update_initial_call_only_sets_last_frame_time(mock_sprites_folder, mock_board):
    """
    Arrange: Create a Graphics object (last_frame_time is None).
    Act: First call to update.
    Assert: Verify last_frame_time is set to now_ms and cur_index does not change.
    """
    # Arrange
    graphics_obj = Graphics(sprites_folder=mock_sprites_folder, board=mock_board)
    graphics_obj.last_frame_time = None # Ensure it's None initially
    initial_index = graphics_obj.cur_index
    now_ms = 1234

    # Act
    graphics_obj.update(now_ms)

    # Assert
    assert graphics_obj.last_frame_time == now_ms
    assert graphics_obj.cur_index == initial_index # Should not change


## בדיקות למתודת `get_img`
#---

@patch('implementation.graphics.Img', new=MockImg) # Apply patch here
def test_get_img_returns_current_sprite(mock_sprites_folder, mock_board):
    """
    Arrange: Create a Graphics object and set cur_index.
    Act: Call get_img.
    Assert: Verify the correct Img object (based on cur_index) is returned.
    """
    # Arrange
    graphics_obj = Graphics(sprites_folder=mock_sprites_folder, board=mock_board)
    graphics_obj.cur_index = 1 # Choose a specific index
    
    expected_img = graphics_obj.sprites[graphics_obj.cur_index]

    # Act
    retrieved_img = graphics_obj.get_img()

    # Assert
    assert retrieved_img is expected_img # Verify the object itself is returned
    assert isinstance(retrieved_img, MockImg)


@patch('implementation.graphics.Img', new=MockImg) # Apply patch here
def test_get_img_on_empty_sprites_list_raises_indexerror(mock_board): # הוסף mock_board לכאן
    """
    Arrange: Create a Graphics object with an empty sprites list.
    Act: Call get_img.
    Assert: Verify IndexError is raised.
    """
    # Arrange
    # Manually initialize Graphics to bypass _load_sprites ValueError for this specific test
    # (כי הפונקציה Graphic.__init__ דורשת תיקייה לא ריקה)
    graphics_obj = Graphics.__new__(Graphics) 
    graphics_obj.sprites_folder = pathlib.Path("dummy") # Set dummy values
    graphics_obj.board = mock_board # השתמש ב-mock_board מה-fixture
    graphics_obj.sprites = [] # Empty list for this test
    graphics_obj.cur_index = 0
    graphics_obj.total_frames = 0 # Must match
    graphics_obj.loop = True
    graphics_obj.fps = 6.0
    graphics_obj.last_frame_time = None

    # Act & Assert
    with pytest.raises(IndexError):
        graphics_obj.get_img()