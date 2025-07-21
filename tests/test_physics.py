import pytest
from implementation.physics import Physics, IdlePhysics, MovePhysics
from implementation.board import Board
from implementation.command import Command


class DummyBoard(Board):
    def __init__(self, cell_W_m=1.0, cell_H_m=1.0):
        self.cell_W_m = cell_W_m
        self.cell_H_m = cell_H_m


def create_cmd(timestamp, piece_id=0, type="Move", params=(1, 1)):
    return Command(timestamp=timestamp, piece_id=piece_id, type=type, params=params)


# ------------------------------
# Physics Base Class Tests
# ------------------------------

def test_physics_initial_position():
    board = DummyBoard()
    p = Physics((2, 3), board)
    assert p.get_pos() == (2.0, 3.0)


def test_physics_reset_stores_command_and_time():
    board = DummyBoard()
    cmd = create_cmd(1234)
    p = Physics((0, 0), board)
    p.reset(cmd)
    assert p.cmd == cmd
    assert p.start_time_ms == 1234


def test_physics_update_returns_command():
    board = DummyBoard()
    cmd = create_cmd(1000)
    p = Physics((0, 0), board)
    p.reset(cmd)
    result = p.update(1500)
    assert result == cmd


def test_physics_capture_flags_are_true():
    p = Physics((0, 0), DummyBoard())
    assert p.can_capture()
    assert p.can_be_captured()


# ------------------------------
# IdlePhysics Tests
# ------------------------------

def test_idle_physics_update_returns_original_command():
    board = DummyBoard()
    cmd = create_cmd(2000)
    p = IdlePhysics((0, 0), board)
    p.reset(cmd)
    result = p.update(3000)
    assert result == cmd


# ------------------------------
# MovePhysics Tests
# ------------------------------

def test_move_physics_reset_sets_vector_and_duration():
    board = DummyBoard(cell_W_m=2.0, cell_H_m=3.0)
    cmd = create_cmd(0, type="Move", params=(2, 3))
    p = MovePhysics((0, 0), board, speed_m_s=1.0)
    p.reset(cmd)
    assert p.vector_m == (4.0, 9.0)
    assert round(p.duration_s, 5) == round((4**2 + 9**2)**0.5 / 1.0, 5)


def test_move_physics_update_interpolates_position():
    board = DummyBoard(cell_W_m=1.0, cell_H_m=1.0)
    cmd = create_cmd(0, type="Move", params=(1, 0))  # move 1m right
    p = MovePhysics((0, 0), board, speed_m_s=1.0)
    p.reset(cmd)
    p.update(500)  # Halfway (0.5s)
    x, y = p.get_pos()
    assert 0.49 <= x <= 0.51
    assert y == 0.0


def test_move_physics_update_sets_final_position():
    board = DummyBoard()
    cmd = create_cmd(0, type="Move", params=(1, 1))
    p = MovePhysics((0, 0), board, speed_m_s=1.0)
    p.reset(cmd)
    p.update(2000)
    x, y = p.get_pos()
    assert x == 1.0
    assert y == 1.0


def test_move_physics_capture_flags_are_false():
    p = MovePhysics((0, 0), DummyBoard())
    assert not p.can_capture()
    assert not p.can_be_captured()


def test_move_physics_invalid_command_raises():
    board = DummyBoard()
    p = MovePhysics((0, 0), board)
    with pytest.raises(ValueError):
        p.reset(Command(timestamp=0, piece_id=0, type="Jump", params=(3, 4)))  # wrong type
    with pytest.raises(ValueError):
        p.reset(Command(timestamp=0, piece_id=0, type="Move", params=(5,)))  # missing param


def test_move_physics_zero_speed_results_in_infinite_duration():
    board = DummyBoard()
    p = MovePhysics((0, 0), board, speed_m_s=0.0)
    cmd = create_cmd(0, type="Move", params=(1, 0))
    p.reset(cmd)
    assert p.duration_s == float("inf")
