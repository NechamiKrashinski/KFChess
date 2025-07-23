# conftest.py
import pytest
import numpy as np
import pathlib
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

# ייבוא המחלקות המקוריות כדי שה-Mocks יוכלו לרשת מהן
from implementation.board import Board
from implementation.img import Img
from implementation.command import Command # לוודא ש-Command מיובא!


# --- Mock Classes ---

class MockImg(Img):
    _read_calls: list = []
    traj: list[tuple[int, int]] = []
    txt_traj: list[tuple[tuple[int, int], str]] = []
    _instance_counter = 0

    def __init__(self):
        # אם Img המקורי מצפה לפרמטרים, ייתכן שתצטרך להוסיף אותם כאן ל-super().__init__()
        # לדוגמה: super().__init__(some_param=value)
        self.img: Optional[np.ndarray] = None
        MockImg._instance_counter += 1
        self._instance_id = MockImg._instance_counter

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        effective_target_size = target_size if target_size is not None else (50, 50)
        self.img = np.copy(np.zeros((effective_target_size[1], effective_target_size[0], 4), dtype=np.uint8))
        MockImg._read_calls.append({'path': path, 'target_size': target_size})
        return self

    def copy(self) -> 'MockImg':
        new_copy = MockImg()
        if self.img is not None:
            new_copy.img = np.copy(self.img)
        return new_copy

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        if self.img is None:
            raise ValueError("Cannot draw: current image is not loaded.")
        if other_img.img is None:
            raise ValueError("Cannot draw on: target image is not loaded.")
        if not (0.0 <= alpha <= 1.0):
            raise ValueError("Alpha must be between 0.0 and 1.0.")
        MockImg.traj.append((x, y))

    def put_text(self, txt: str, x: int, y: int, font_size: float, *args, **kwargs):
        MockImg.txt_traj.append(((x, y), txt))

    def show(self):
        pass

    def resize(self, new_width: int, new_height: int):
        if self.img is None:
            raise ValueError("Cannot resize: no image has been loaded yet.")
        if new_width <= 0 or new_height <= 0:
            raise ValueError("New width and height must be positive.")
        self.img = np.zeros((new_height, new_width, 4), dtype=np.uint8)

    def get_width(self) -> int:
        return self.img.shape[1] if self.img is not None else 0

    def get_height(self) -> int:
        return self.img.shape[0] if self.img is not None else 0

    @classmethod
    def reset(cls):
        cls._read_calls = []
        cls.traj.clear()
        cls.txt_traj.clear()
        cls._instance_counter = 0

    @classmethod
    def get_read_calls(cls) -> list:
        return cls._read_calls

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MockImg):
            return NotImplemented
        if self.img is None and other.img is None:
            return True
        if self.img is None or other.img is None:
            return False
        return np.array_equal(self.img, other.img)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __repr__(self) -> str:
        if self.img is not None:
            return f"MockImg(shape={self.img.shape}, id={self._instance_id})"
        return f"MockImg(uninitialized, id={self._instance_id})"


class MockBoard(Board):
    def __init__(self, cell_W_pix: int = 50, cell_H_pix: int = 50, 
                 cell_W_m: float = 1.0, cell_H_m: float = 1.0,
                 W_cells: int = 10, H_cells: int = 10, # הוסף את אלה!
                 img: Optional['MockImg'] = None): # הוסף גם את img כאן עם default None
        
        # אם img לא סופק, צור MockImg חדש
        if img is None:
            img = MockImg()

        super().__init__(
            cell_H_pix=cell_H_pix,
            cell_W_pix=cell_W_pix,
            cell_H_m=cell_H_m,
            cell_W_m=cell_W_m,
            W_cells=W_cells, # העבר את הפרמטרים שהתקבלו
            H_cells=H_cells, # העבר את הפרמטרים שהתקבלו
            img=img # העבר את האובייקט img שהתקבל או נוצר
        )

    # השאר את מתודת clone כפי שהיא כרגע
    def clone(self) -> 'MockBoard':
        new_img = self.img.copy() 
        return MockBoard(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=new_img
        )

    def get_dimensions(self) -> Tuple[float, float]:
        return (self.cell_W_pix, self.cell_H_pix)

    def get_cell_dimensions_m(self) -> Tuple[float, float]:
        return (self.cell_W_m, self.cell_H_m)


@dataclass
class MockCommand(Command):
    # כאשר יורשים מ-dataclass אחר, ורוצים לשנות את ברירת המחדל
    # של שדה שכבר קיים במחלקת האב, או להוסיף שדות חדשים עם ברירת מחדל,
    # חייבים לשמור על הכלל: שדות ללא ברירת מחדל (כולל אלה שירשנו)
    # יופיעו לפני שדות עם ברירת מחדל (גם אלה שירשנו ושינינו, או חדשים).

    # מחלקת Command המקורית שלך היא:
    # timestamp: int
    # piece_id: str
    # type: str
    # params: List

    # כל אלו הם שדות חובה (ללא ברירת מחדל) במחלקת האב.
    # לכן, אם נגדיר אותם שוב ב-MockCommand כ-dataclass
    # וניתן לאחד מהם ברירת מחדל, זה ישבור את הכלל אם שדה חובה יגיע אחריו.

    # הבעיה הספציפית: "non-default argument 'command_type' follows default argument 'params'"
    # זה קרה כי ניסית להוסיף את 'command_type' כשדה חובה אחרי 'params' שכנראה קיבל ברירת מחדל.

    # הפתרון הטוב ביותר: אם אתה לא רוצה לשנות את ה-Command המקורי,
    # ואתה רק רוצה לייצר מופעים של MockCommand לצורך בדיקה,
    # אל תגדיר מחדש את השדות שכבר קיימים במחלקת האב (Command) ב-MockCommand,
    # אלא אם כן אתה באמת צריך לשנות להם את ערכי ברירת המחדל.
    # אם אתה רוצה ש'params' יהיה עם ברירת מחדל ב-MockCommand, אבל לא ב-Command המקורי,
    # וש'type' ייקרא 'command_type' ועדיין יהיה חובה, הנה הדרך:

    # ראשית, כל השדות שהם ללא ברירת מחדל במחלקת האב:
    # (timestamp, piece_id, type)
    # אותם אנחנו רוצים להוריש כמות שהם, בלי לשנות להם את התנהגות ה-dataclass.
    # אנחנו לא נרשום אותם שוב.

    # שדה 'params' מ-Command: הוא שדה חובה במקור.
    # אם ב-MockCommand אתה רוצה שהוא יהיה עם ברירת מחדל, הוא צריך להיות מוגדר פה
    # (ואז הוא הופך לשדה ברירת מחדל ב-MockCommand),
    # וכל שדה אחריו חייב להיות גם עם ברירת מחדל.
    params: List = field(default_factory=list)

    # הוספה של 'command_type' כשדה נפרד ב-MockCommand (אם הוא לא אמור לדרוס את 'type' המקורי),
    # או טיפול ב'type' המקורי.
    # הדרך הכי נקייה היא לא להגדיר שדות בכלל ב-MockCommand, אלא אם הם חדשים.
    # אם 'command_type' זה בעצם ה-'type' של Command, פשוט השתמש בשם המקורי שלו.

    # בגלל השגיאה הספציפית שקיבלת: "non-default argument 'command_type' follows default argument 'params'",
    # אני מסיק ש:
    # 1. 'params' קיבל ברירת מחדל ב-MockCommand (כמו field(default_factory=list)).
    # 2. 'command_type' (שמקורו ב-'type' של Command) הוגדר ב-MockCommand כחובה (ללא ברירת מחדל).
    # וזה הקונפליקט.

    # הפתרון: וודא ש'command_type' (שהוא 'type' מהמקור) לא מוגדר ב-MockCommand.
    # הוא יירש אוטומטית כ-non-default argument.
    # וש-params יוגדר עם default_factory רק אם הוא מופיע אחרי כל שדות ה-non-default.

    # אם אתה רוצה ש-MockCommand יאפשר אתחול קל יותר בלי לדרוש את params,
    # אבל Command המקורי דורש אותו:
    # אתה יכול לרשת מ-Command אבל לא להיות dataclass בעצמך,
    # או להשתמש ב-MagicMock בבדיקות.

    # נחזור לפתרון הכי סביר ופשוט עבור `MockCommand` כ-dataclass יורש:
    # אל תגדיר שוב שדות שכבר קיימים ב-Command.
    # אם `Command` הוא: (timestamp, piece_id, type, params) וכולם חובה,
    # ו-`MockCommand` הוא גם `dataclass` ואין לו שדות *חדשים* עם ברירת מחדל,
    # אז `MockCommand` יכול פשוט להיות ריק.
    # הבעיה נוצרה כאשר ניסית לתת ברירת מחדל ל-'params' או ל-'piece_id'
    # ואז להוסיף 'command_type' כשדה חובה.

    # אם תרצה ש-`params` יהיה עם ברירת מחדל ב-`MockCommand` בלבד:
    # params: List = field(default_factory=list)
    #
    # אבל אז, אם `type` הוא עדיין שדה חובה, הוא יצטרך לבוא לפני `params`
    # (מה שסותר את הרישום של `Command`).

    # הדרך הפשוטה ביותר היא להניח ש-MockCommand פשוט יורש את כל השדות מ-Command
    # כפי שהם, ורק אם יש שדה *חדש* ש-MockCommand מוסיף (או שדה קיים שמקבל ברירת מחדל *ב-MockCommand בלבד*),
    # אז נגדיר אותו.
    #
    # נסה את זה:
    # תמחק את כל השדות מתוך MockCommand. הוא יירש את כולם מ-Command.
    pass # השאר את זה ריק לגמרי!


# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_mocks_fixture():
    """Resets the recorded data in MockImg for fresh tests."""
    MockImg.reset()
    yield


@pytest.fixture
def mock_sprites_folder(tmp_path: pathlib.Path):
    """
    Creates a temporary sprites folder with a few dummy PNG files.
    """
    sprites_path = tmp_path / "sprites"
    sprites_path.mkdir()

    for i in range(3):
        (sprites_path / f"sprite_{i:02d}.png").touch()
    return sprites_path


@pytest.fixture
def empty_mock_sprites_folder(tmp_path: pathlib.Path):
    """Creates a temporary empty sprites folder."""
    sprites_path = tmp_path / "empty_sprites"
    sprites_path.mkdir()
    return sprites_path


@pytest.fixture
def mock_board():
    """Fixture to provide a default MockBoard instance."""
    return MockBoard()

@pytest.fixture
def default_board():
    """Fixture to provide a default MockBoard instance for Physics tests."""
    return MockBoard(cell_W_m=1.0, cell_H_m=1.0)

@pytest.fixture
def large_cell_board():
    """Fixture to provide a MockBoard with larger cell dimensions for Physics tests."""
    return MockBoard(cell_W_m=10.0, cell_H_m=10.0)

@pytest.fixture
def MockCommand_class():
    """Fixture to provide the MockCommand class itself for tests that need to instantiate it."""
    return MockCommand