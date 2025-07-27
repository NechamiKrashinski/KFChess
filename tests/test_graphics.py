import pytest
from implementation.command import Command


# ---------- SANITY TESTS ----------

def test_create_command_with_required_fields():
    # Arrange
    timestamp = 1234
    piece_id = "knight_1"
    cmd_type = "Move"
    params = [(1, 2), (3, 4)]

    # Act
    cmd = Command(
        timestamp=timestamp,
        piece_id=piece_id,
        type=cmd_type,
        params=params
    )

    # Assert
    assert cmd.timestamp == timestamp
    assert cmd.piece_id == piece_id
    assert cmd.type == cmd_type
    assert cmd.params == params
    assert cmd.source_cell is None


def test_create_command_with_optional_source_cell():
    # Arrange
    source = (5, 5)

    # Act
    cmd = Command(
        timestamp=0,
        piece_id="bishop_7",
        type="Jump",
        params=[(5, 5), (7, 7)],
        source_cell=source
    )

    # Assert
    assert cmd.source_cell == source


def test_command_fields_are_accessible_and_mutable():
    # Arrange
    cmd = Command(
        timestamp=1000,
        piece_id="pawn_3",
        type="Move",
        params=[(1, 1), (1, 2)]
    )

    # Act
    cmd.type = "Jump"
    cmd.params = [(1, 1), (3, 3)]
    cmd.source_cell = (1, 1)

    # Assert
    assert cmd.type == "Jump"
    assert cmd.params == [(1, 1), (3, 3)]
    assert cmd.source_cell == (1, 1)


# ---------- EDGE CASES ----------

def test_command_with_empty_params_list_is_valid():
    # Arrange & Act
    cmd = Command(
        timestamp=0,
        piece_id="king_1",
        type="Idle",
        params=[]
    )

    # Assert
    assert isinstance(cmd, Command)
    assert cmd.params == []


def test_command_with_unexpected_type_value():
    # Arrange
    invalid_type = "Teleport"

    # Act
    cmd = Command(
        timestamp=0,
        piece_id="rook_1",
        type=invalid_type,
        params=[]
    )

    # Assert
    assert cmd.type == "Teleport"  # allowed at runtime; semantic validation is external
