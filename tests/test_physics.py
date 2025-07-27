import pytest
from implementation.mock_img import MockImg
from implementation.board import Board  # תחליף לנתיב האמיתי שלך
from implementation.command import Command  # תחליף לנתיב האמיתי שלך
from implementation.physics import Physics, IdlePhysics, MovePhysics, JumpPhysics


@pytest.fixture
def board_with_mockimg():
    img = MockImg()
    # נניח שה-board שלך דורש פרמטרים אלה:
    return Board(
        cell_H_pix=10,
        cell_W_pix=10,
        cell_H_m=1.0,
        cell_W_m=1.0,
        W_cells=8,
        H_cells=8,
        img=img
    )


def test_physics_initialization(board_with_mockimg):
    p = Physics(start_cell=(1, 2), board=board_with_mockimg, speed_m_s=2.0)
    assert p.cur_pos_m == (1.0 * board_with_mockimg.cell_W_m, 2.0 * board_with_mockimg.cell_H_m)
    assert p.speed == 2.0
    assert p.get_cell() == (1, 2)


def test_idle_physics_update_returns_none(board_with_mockimg):
    p = IdlePhysics(start_cell=(0, 0), board=board_with_mockimg)
    assert p.update(1000) is None


def test_move_physics_reset_and_update(board_with_mockimg):
    cmd = Command(timestamp=1000, type="Move", piece_id="p1", params=[3, 4], source_cell=(1, 1))
    mp = MovePhysics(start_cell=(1, 1), board=board_with_mockimg, speed_m_s=1.0)
    mp.reset(cmd)
    
    assert mp.end_cell == (3, 4)
    assert mp.start_cell == (1, 1)
    assert mp.duration_s > 0
    
    # לפני התחלת הזמן
    assert mp.update(999) is None
    
    # באמצע התנועה (חצי מהזמן)
    mid_time = mp.start_time_ms + int(mp.duration_s * 500)
    assert mp.update(mid_time) is None
    
    # לאחר סיום התנועה
    end_time = mp.start_time_ms + int(mp.duration_s * 1000) + 1
    finished_cmd = mp.update(end_time)
    assert finished_cmd is not None
    assert finished_cmd.type == "finished_movement"
    assert finished_cmd.piece_id == "p1"


def test_move_physics_reset_invalid_command(board_with_mockimg):
    mp = MovePhysics(start_cell=(0, 0), board=board_with_mockimg)
    # פקודה עם סוג לא נכון
    bad_cmd = Command(timestamp=1000, type="Jump", piece_id="p1", params=[1, 2])
    with pytest.raises(ValueError):
        mp.reset(bad_cmd)
    
    # פקודה עם פרמטרים לא נכונים
    bad_cmd2 = Command(timestamp=1000, type="Move", piece_id="p1", params=["a", 2])
    with pytest.raises(ValueError):
        mp.reset(bad_cmd2)


def test_jump_physics_reset_and_update(board_with_mockimg):
    cmd = Command(timestamp=1000, type="Jump", piece_id="p2", params=[5, 6], source_cell=(2, 2))
    jp = JumpPhysics(start_cell=(2, 2), board=board_with_mockimg)
    jp.reset(cmd)
    
    assert jp.end_cell == (5, 6)
    assert jp.start_cell == (2, 2)
    assert jp.duration_s == 1  # כפי שמוגדר ב-JumpPhysics.reset

    # לפני התחלת הזמן
    assert jp.update(999) is None
    
    # לאחר סיום התנועה (כל הזמן = 1 שניה)
    finished_cmd = jp.update(jp.start_time_ms + 1000)
    assert finished_cmd is not None
    assert finished_cmd.type == "finished_jump"
    assert finished_cmd.piece_id == "p2"


def test_can_be_captured_and_can_capture_methods(board_with_mockimg):
    p = Physics(start_cell=(0, 0), board=board_with_mockimg)
    assert p.can_be_captured() is True
    assert p.can_capture() is False

    mp = MovePhysics(start_cell=(0, 0), board=board_with_mockimg)
    assert mp.can_be_captured() is False
    assert mp.can_capture() is True

    jp = JumpPhysics(start_cell=(0, 0), board=board_with_mockimg)
    assert jp.can_be_captured() is False
    assert jp.can_capture() is True
