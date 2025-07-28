import numpy as np
import cv2
import pytest
from implementation.piece import Piece
from implementation.command import Command

# Dummy classes for testing Piece without תלות ביישומים החיצוניים

class DummyPhysics:
    def get_cell(self):
        return (1, 2)
    def get_pos(self):
        return (1.0, 2.0)

class DummyGraphics:
    def __init__(self, state_name="idle"):
        class DummyFolder:
            def __init__(self, name):
                self.name = name
        # graphics עם שם מצב "idle"
        self.sprites_folder = type("DummyParent", (), {"parent": DummyFolder(state_name)})
    def get_img(self):
        # תמונה ריקה בגודל 50x50 עם 4 ערוצים
        img = np.zeros((50,50,4), dtype=np.uint8)
        # נדרשת implement צלמית מינימלית
        return type("DummyImg", (), {
            "img": img,
            "copy": lambda self: self,
            "draw_on": lambda self, other_img, x, y, alpha=1.0: None,
            "get_width": lambda self: 50,
            "get_height": lambda self: 50
        })()

class DummyMoves:
    def get_moves(self, r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color):
        # מחזיר תנועה דמיונית: תאים סמוכים
        return [(r+1, c), (r, c+1)]

class DummyState:
    def __init__(self):
        self.physics = DummyPhysics()
        self.graphics = DummyGraphics()
        self.moves = DummyMoves()
    def process_command(self, cmd, now_ms):
        return self
    def update(self, now_ms):
        return self
    def reset(self, cmd):
        pass
    def get_command(self):
        return None
    def can_transition(self, now_ms):
        return True
    def get_graphics(self):
        return self.graphics
    def get_physics(self):
        return self.physics
    def get_moves(self):
        return self.moves
    def get_state(self):
        return "idle"

# נשתמש במחלקת Command המקורית - DummyCommand לא משנה דבר כאן
class DummyCommand(Command):
    pass

@pytest.fixture
def dummy_state():
    return DummyState()

@pytest.fixture
def piece(dummy_state):
    # יצירת כלי עם piece_id "pW" (למשל, 'pW' – p=pawn, W=color white)
    return Piece(piece_id='pW', init_state=dummy_state, color='white')

def test_get_color(piece):
    # בודק אם get_color מחזיר את הצבע הנכון
    assert piece.get_color() == 'white'

def test_get_type_piece(piece):
    # מצפים שהאות הראשונה של piece_id תהיה אות גדולה
    assert piece.get_type_piece() == 'P'

def test_get_moves(piece):
    # שיטת get_moves משתמשת ב-DummyMoves שמחזירה את [(r+1, c), (r, c+1)]
    # עם current cell מתוך DummyPhysics (1,2)
    moves = piece.get_moves([piece])
    expected = [(2,2), (1,3)]
    assert moves == expected

# ...existing code can be extended with tests נוספים עבור on_command, update, draw_on_board וכו' אם נדרש...