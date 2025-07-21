import pytest
from types import SimpleNamespace
from implementation.physics_factory import PhysicsFactory
from implementation.physics import Physics
from implementation.board import Board


@pytest.fixture
def dummy_board():
    return Board(
        cell_H_pix=100,
        cell_W_pix=100,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=SimpleNamespace(img=None)  # לא רלוונטי לפיזיקה
    )


def test_create_default_speed(dummy_board):
    factory = PhysicsFactory(dummy_board)
    start_cell = (3, 4)
    physics = factory.create(start_cell, cfg={})

    assert isinstance(physics, Physics)
    assert physics.start_cell == start_cell
    assert physics.board is dummy_board
    assert physics.speed == 1.0
    assert physics.get_pos() == (3, 4)


def test_create_with_custom_speed(dummy_board):
    factory = PhysicsFactory(dummy_board)
    physics = factory.create((0, 0), cfg={"speed": 2.5})

    assert physics.speed == 2.5


def test_create_negative_cell(dummy_board):
    factory = PhysicsFactory(dummy_board)
    with pytest.raises(ValueError, match="out of board bounds"):
        factory.create((-1, 0), cfg={})


def test_create_cell_out_of_bounds(dummy_board):
    factory = PhysicsFactory(dummy_board)
    # 8 is out of bounds (indexing from 0)
    with pytest.raises(ValueError, match="out of board bounds"):
        factory.create((8, 5), cfg={})


def test_create_cell_type_error(dummy_board):
    factory = PhysicsFactory(dummy_board)

    with pytest.raises(ValueError, match="start_cell must be a"):
        factory.create("A1", cfg={})

    with pytest.raises(ValueError, match="start_cell must be a"):
        factory.create([1, 2], cfg={})

    with pytest.raises(ValueError, match="start_cell must be a"):
        factory.create((1,), cfg={})


def test_create_cfg_ignores_irrelevant_keys(dummy_board):
    factory = PhysicsFactory(dummy_board)
    physics = factory.create((1, 1), cfg={"foo": "bar", "speed": 1.5})

    assert physics.speed == 1.5
    assert not hasattr(physics, "foo")


def test_position_calculation_correct(dummy_board):
    factory = PhysicsFactory(dummy_board)

    # board cell 5,6 with 1 meter per cell -> should map to (5,6)
    physics = factory.create((5, 6), cfg={})
    assert physics.get_pos() == (5.0, 6.0)


def test_position_calculation_with_non_square_cells():
    board = Board(
        cell_H_pix=50,
        cell_W_pix=80,
        cell_H_m=2,
        cell_W_m=3,
        W_cells=10,
        H_cells=10,
        img=SimpleNamespace(img=None)
    )

    factory = PhysicsFactory(board)

    physics = factory.create((2, 3), cfg={})
    # expect position: x = 2 * 3 = 6, y = 3 * 2 = 6
    assert physics.get_pos() == (6, 6)


def test_different_cells_produce_different_positions(dummy_board):
    factory = PhysicsFactory(dummy_board)

    p1 = factory.create((0, 0), cfg={})
    p2 = factory.create((1, 0), cfg={})
    p3 = factory.create((0, 1), cfg={})

    assert p1.get_pos() != p2.get_pos()
    assert p1.get_pos() != p3.get_pos()
    assert p2.get_pos() != p3.get_pos()


def test_speed_defaults_and_override(dummy_board):
    factory = PhysicsFactory(dummy_board)

    default = factory.create((1, 1), cfg={})
    fast = factory.create((1, 1), cfg={"speed": 5.0})
    slow = factory.create((1, 1), cfg={"speed": 0.1})

    assert default.speed == 1.0
    assert fast.speed == 5.0
    assert slow.speed == 0.1
