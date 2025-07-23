# tests/test_physics.py
import pytest
from unittest.mock import MagicMock, patch
from typing import Tuple

# ייבוא המחלקות המקוריות הנבדקות
from implementation.board import Board
from implementation.command import Command
from implementation.physics import Physics, IdlePhysics, MovePhysics

# ייבוא MockBoard, MockCommand מ-conftest.py
from .conftest import MockBoard, MockCommand, MockCommand_class


# נמק את Board ואת Command עבור כל הבדיקות בקובץ זה
# @patch ('implementation.physics.Board', new=MockBoard) # ניתן למק באופן גלובלי או בודד לכל מחלקה
# @patch ('implementation.physics.Command', new=MockCommand) 

class TestPhysics:
    @pytest.fixture
    def mock_board_physics(self):
        # פיקסטור ל-MockBoard עם ערכים ספציפיים לבדיקות פיזיקה
        # חשוב ש-cell_W_m ו-cell_H_m יהיו שונים מ-0
        return MockBoard(cell_W_pix=50, cell_H_pix=50, cell_W_m=1.0, cell_H_m=1.0, W_cells=10, H_cells=10)

    @pytest.mark.parametrize("start_cell, speed, expected_initial_pos_m", [
        ((0, 0), 1.0, (0.0, 0.0)),
        ((1, 1), 0.5, (1.0, 1.0)), # assuming cell_W_m=1.0, cell_H_m=1.0
        ((5, 8), 2.0, (5.0, 8.0)),
    ])
    def test_physics_init_sanity_sets_attributes_correctly(self, mock_board_physics, start_cell, speed, expected_initial_pos_m):
        """
        Arrange: Define initial parameters.
        Act: Initialize Physics object.
        Assert: Verify all attributes are set correctly, especially cur_pos_m calculation.
        """
        # Arrange (parameters are from @parametrize and fixture)

        # Act
        physics_obj = Physics(start_cell=start_cell, board=mock_board_physics, speed_m_s=speed)

        # Assert
        assert physics_obj.board is mock_board_physics
        assert physics_obj.speed == speed
        assert physics_obj.start_cell == start_cell
        assert physics_obj.cmd is None
        assert physics_obj.start_time_ms is None
        assert physics_obj.cur_pos_m == expected_initial_pos_m
        assert physics_obj.target_cell == start_cell


    @pytest.mark.parametrize("start_cell, invalid_speed, expected_error_match", [
        ((0, 0), 0.0, None), # 0 speed is allowed for Physics (MovePhysics handles it)
        ((0, 0), -1.0, None), # Negative speed is allowed for Physics (MovePhysics handles it)
    ])
    def test_physics_init_with_invalid_speed_is_allowed(self, mock_board_physics, start_cell, invalid_speed, expected_error_match):
        """
        Arrange: Provide invalid speed to Physics init.
        Act: Initialize Physics object.
        Assert: Verify it doesn't raise an error at this level (MovePhysics handles speed 0 for duration).
        """
        # Arrange (parameters from @parametrize and fixture)

        # Act
        physics_obj = Physics(start_cell=start_cell, board=mock_board_physics, speed_m_s=invalid_speed)

        # Assert
        assert physics_obj.speed == invalid_speed # Should simply accept the value


    def test_physics_reset_updates_command_and_start_time(self, mock_board_physics, MockCommand_class):
        """
        Arrange: Create Physics object and a mock Command.
        Act: Call reset with the command.
        Assert: Verify cmd and start_time_ms are updated.
        """
        # Arrange
        physics_obj = Physics(start_cell=(0, 0), board=mock_board_physics)
        mock_cmd = MockCommand_class(timestamp=1234, piece_id="p1", type="idle", params=[])

        # Act
        physics_obj.reset(mock_cmd)

        # Assert
        assert physics_obj.cmd is mock_cmd
        assert physics_obj.start_time_ms == mock_cmd.timestamp


    def test_physics_update_returns_current_command(self, mock_board_physics, MockCommand_class):
        """
        Arrange: Create Physics object and set a command.
        Act: Call update.
        Assert: Verify the stored command is returned.
        """
        # Arrange
        physics_obj = Physics(start_cell=(0, 0), board=mock_board_physics)
        mock_cmd = MockCommand_class(timestamp=100, piece_id="p1", type="move", params=[])
        physics_obj.cmd = mock_cmd # Manually set cmd for this test

        # Act
        returned_cmd = physics_obj.update(now_ms=200)

        # Assert
        assert returned_cmd is mock_cmd


    def test_physics_can_be_captured_returns_true_by_default(self, mock_board_physics):
        """
        Arrange: Create Physics object.
        Act: Call can_be_captured.
        Assert: Verify it returns True (default behavior).
        """
        # Arrange
        physics_obj = Physics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = physics_obj.can_be_captured()

        # Assert
        assert result is True


    def test_physics_can_capture_returns_false_by_default(self, mock_board_physics):
        """
        Arrange: Create Physics object.
        Act: Call can_capture.
        Assert: Verify it returns False (default behavior).
        """
        # Arrange
        physics_obj = Physics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = physics_obj.can_capture()

        # Assert
        assert result is False


    def test_physics_get_pos_returns_current_metric_position(self, mock_board_physics):
        """
        Arrange: Create Physics object.
        Act: Call get_pos.
        Assert: Verify the initial metric position is returned correctly.
        """
        # Arrange
        start_cell = (2, 3)
        # Using mock_board_physics with cell_W_m=1.0, cell_H_m=1.0
        physics_obj = Physics(start_cell=start_cell, board=mock_board_physics)

        # Act
        pos = physics_obj.get_pos()

        # Assert
        # Initial pos should be (start_cell[0] * cell_W_m, start_cell[1] * cell_H_m)
        assert pos == (start_cell[0] * mock_board_physics.cell_W_m, start_cell[1] * mock_board_physics.cell_H_m)


    @pytest.mark.parametrize("cur_pos_m, expected_cell", [
        ((0.0, 0.0), (0, 0)),
        ((0.9, 0.9), (0, 0)), # Still within cell (0,0)
        ((1.0, 1.0), (1, 1)), # Exact cell boundary
        ((1.5, 2.5), (1, 2)), # Middle of cell
        ((9.9, 9.9), (9, 9)), # Last cell
    ])
    def test_physics_get_cell_returns_current_cell(self, mock_board_physics, cur_pos_m, expected_cell):
        """
        Arrange: Create Physics object and manually set cur_pos_m.
        Act: Call get_cell.
        Assert: Verify the correct integer cell coordinates are returned.
        """
        # Arrange
        physics_obj = Physics(start_cell=(0, 0), board=mock_board_physics)
        physics_obj.cur_pos_m = cur_pos_m # Manually set current metric position

        # Act
        cell = physics_obj.get_cell()

        # Assert
        assert cell == expected_cell


    @pytest.mark.parametrize("target_cell, custom_speed", [
        ((5, 5), 1.0),
        ((0, 0), 2.0),
        ((7, 2), 0.5),
    ])
    def test_physics_create_movement_to_returns_movephysics(self, mock_board_physics, target_cell, custom_speed):
        """
        Arrange: Create Physics object.
        Act: Call create_movement_to.
        Assert: Verify a new MovePhysics instance is returned with correct initial state.
        """
        # Arrange
        start_cell_original = (1, 1)
        physics_obj = Physics(start_cell=start_cell_original, board=mock_board_physics)
        
        # Act
        move_physics_obj = physics_obj.create_movement_to(target_cell=target_cell, speed=custom_speed)

        # Assert
        assert isinstance(move_physics_obj, MovePhysics)
        assert move_physics_obj.start_cell == start_cell_original # Should use current cell of original physics
        assert move_physics_obj.board is mock_board_physics
        assert move_physics_obj.speed == custom_speed
        assert move_physics_obj.end_cell == target_cell # The end_cell is explicitly set in create_movement_to

        # Ensure MovePhysics's own init defaults for vector/duration are still in place
        assert move_physics_obj.vector_m == (0.0, 0.0) 
        assert move_physics_obj.duration_s == 0.0
        assert move_physics_obj.cur_pos_m == (start_cell_original[0] * mock_board_physics.cell_W_m,
                                              start_cell_original[1] * mock_board_physics.cell_H_m)


class TestIdlePhysics:
    @pytest.fixture
    def mock_board_physics(self):
        return MockBoard(cell_W_pix=50, cell_H_pix=50, cell_W_m=1.0, cell_H_m=1.0, W_cells=10, H_cells=10)

    def test_idle_physics_inherits_from_physics(self, mock_board_physics):
        """
        Arrange: None.
        Act: Create IdlePhysics object.
        Assert: Verify it's an instance of both IdlePhysics and Physics.
        """
        # Arrange
        # Act
        idle_obj = IdlePhysics(start_cell=(0, 0), board=mock_board_physics)

        # Assert
        assert isinstance(idle_obj, IdlePhysics)
        assert isinstance(idle_obj, Physics)


    def test_idle_physics_update_returns_command_without_changing_position(self, mock_board_physics, MockCommand_class):
        """
        Arrange: Create IdlePhysics object with a command and initial position.
        Act: Call update multiple times.
        Assert: Verify the command is returned, and position remains unchanged.
        """
        # Arrange
        start_cell = (3, 4)
        initial_pos_m = (start_cell[0] * mock_board_physics.cell_W_m, start_cell[1] * mock_board_physics.cell_H_m)
        idle_obj = IdlePhysics(start_cell=start_cell, board=mock_board_physics)
        
        mock_cmd = MockCommand_class(timestamp=100, piece_id="p1", type="idle", params=[])
        idle_obj.reset(mock_cmd) # Set the command

        # Act & Assert
        # First update
        returned_cmd_1 = idle_obj.update(now_ms=200)
        assert returned_cmd_1 is mock_cmd
        assert idle_obj.get_pos() == initial_pos_m
        assert idle_obj.get_cell() == start_cell

        # Second update (later time)
        returned_cmd_2 = idle_obj.update(now_ms=500)
        assert returned_cmd_2 is mock_cmd
        assert idle_obj.get_pos() == initial_pos_m
        assert idle_obj.get_cell() == start_cell


    def test_idle_physics_can_be_captured_returns_true(self, mock_board_physics):
        """
        Arrange: Create IdlePhysics object.
        Act: Call can_be_captured.
        Assert: Verify it returns True (as it's idle).
        """
        # Arrange
        idle_obj = IdlePhysics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = idle_obj.can_be_captured()

        # Assert
        assert result is True


    def test_idle_physics_can_capture_returns_false(self, mock_board_physics):
        """
        Arrange: Create IdlePhysics object.
        Act: Call can_capture.
        Assert: Verify it returns False (as it's idle).
        """
        # Arrange
        idle_obj = IdlePhysics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = idle_obj.can_capture()

        # Assert
        assert result is False




class TestMovePhysics:
    @pytest.fixture
    def mock_board_physics(self):
        # Set cell dimensions to 1.0m for simpler calculations
        return MockBoard(cell_W_pix=50, cell_H_pix=50, cell_W_m=1.0, cell_H_m=1.0, W_cells=10, H_cells=10)

    @pytest.mark.parametrize("start_cell, speed", [
        ((0, 0), 1.0),
        ((2, 3), 0.5),
        ((8, 8), 10.0),
    ])
    def test_move_physics_init_sanity_sets_attributes_correctly(self, mock_board_physics, start_cell, speed):
        """
        Arrange: Define initial parameters.
        Act: Initialize MovePhysics object.
        Assert: Verify all attributes are set correctly, including inherited ones and new ones.
        """
        # Arrange (parameters are from @parametrize and fixture)

        # Act
        move_obj = MovePhysics(start_cell=start_cell, board=mock_board_physics, speed_m_s=speed)

        # Assert
        assert isinstance(move_obj, MovePhysics)
        assert isinstance(move_obj, Physics)
        assert move_obj.board is mock_board_physics
        assert move_obj.speed == speed
        assert move_obj.start_cell == start_cell
        assert move_obj.cmd is None
        assert move_obj.start_time_ms is None
        assert move_obj.cur_pos_m == (start_cell[0] * mock_board_physics.cell_W_m, start_cell[1] * mock_board_physics.cell_H_m)
        assert move_obj.target_cell == start_cell # From super().__init__

        # New attributes specific to MovePhysics
        assert move_obj.end_cell == start_cell # Initialized to start_cell
        assert move_obj.vector_m == (0.0, 0.0)
        assert move_obj.duration_s == 0.0


    @pytest.mark.parametrize("cmd_type, params, expected_error_match", [
        ("Idle", [], "Invalid command for MovePhysics"), # Wrong type
        ("Move", [], "Invalid command for MovePhysics"), # Wrong number of params (0 instead of 2)
        ("Move", ["a", "b"], "Invalid command for MovePhysics"), # Wrong type for params (not int tuples)
        ("Move", [1, "b"], "Invalid command for MovePhysics"), # Mixed type params
        ("Move", [1, 2, 3], "Invalid command for MovePhysics"), # Too many params
    ])
    def test_move_physics_reset_invalid_command_raises_valueerror(self, mock_board_physics, MockCommand_class, cmd_type, params, expected_error_match):
        """
        Arrange: Create MovePhysics object and an invalid mock Command.
        Act: Call reset with the invalid command.
        Assert: Verify ValueError is raised.
        """
        # Arrange
        move_obj = MovePhysics(start_cell=(0, 0), board=mock_board_physics)
        mock_cmd = MockCommand_class(timestamp=100, piece_id="p1", type=cmd_type, params=params)

        # Act & Assert
        with pytest.raises(ValueError, match=expected_error_match):
            move_obj.reset(mock_cmd)


    @pytest.mark.parametrize("start_cell, end_cell, speed, timestamp, expected_vector_m, expected_duration_s", [
        # Horizontal movement
        ((0, 0), (5, 0), 1.0, 100, (5.0, 0.0), 5.0), # 5m distance, 1m/s speed -> 5s duration
        ((5, 0), (0, 0), 1.0, 100, (-5.0, 0.0), 5.0),
        # Vertical movement
        ((0, 0), (0, 5), 1.0, 100, (0.0, 5.0), 5.0),
        ((0, 5), (0, 0), 1.0, 100, (0.0, -5.0), 5.0),
        # Diagonal movement (3-4-5 triangle)
        ((0, 0), (3, 4), 1.0, 100, (3.0, 4.0), 5.0), # distance sqrt(3^2+4^2) = 5
        ((0, 0), (3, 4), 2.5, 100, (3.0, 4.0), 2.0), # distance 5, speed 2.5 -> 2s
        # No movement
        ((0, 0), (0, 0), 1.0, 100, (0.0, 0.0), 0.0),
        # Speed 0 - duration should be infinity
        ((0, 0), (1, 0), 0.0, 100, (1.0, 0.0), float('inf')),
    ])
    def test_move_physics_reset_calculates_movement_params_correctly(self, mock_board_physics, MockCommand_class,
                                                                       start_cell, end_cell, speed, timestamp,
                                                                       expected_vector_m, expected_duration_s):
        """
        Arrange: Create MovePhysics object.
        Act: Call reset with a valid 'Move' command.
        Assert: Verify cmd, start_time_ms, start_cell, end_cell, vector_m, and duration_s are set correctly.
        """
        # Arrange
        move_obj = MovePhysics(start_cell=start_cell, board=mock_board_physics, speed_m_s=speed)
        # MockCommand_class provides a command that will be used by reset
        mock_cmd = MockCommand_class(timestamp=timestamp, piece_id="p1", type="Move", params=list(end_cell))

        # Act
        move_obj.reset(mock_cmd)

        # Assert
        assert move_obj.cmd is mock_cmd
        assert move_obj.start_time_ms == timestamp
        assert move_obj.start_cell == start_cell # start_cell is updated to current get_cell()
        assert move_obj.end_cell == end_cell
        
        # Using pytest.approx for float comparisons
        assert move_obj.vector_m[0] == pytest.approx(expected_vector_m[0])
        assert move_obj.vector_m[1] == pytest.approx(expected_vector_m[1])
        assert move_obj.duration_s == pytest.approx(expected_duration_s)


    @pytest.mark.parametrize("initial_pos_m, start_cell, end_cell, speed, start_time_ms, now_ms, expected_pos_m, expected_cell", [
        # No movement yet (elapsed_s < duration_s)
        ((0.0, 0.0), (0, 0), (1, 0), 1.0, 0, 500, (0.5, 0.0), (0, 0)), # Halfway in 0.5s for 1m move
        ((0.0, 0.0), (0, 0), (0, 1), 1.0, 0, 250, (0.0, 0.25), (0, 0)), # Quarterway
        # Movement completed (elapsed_s >= duration_s)
        ((0.0, 0.0), (0, 0), (1, 0), 1.0, 0, 1000, (1.0, 0.0), (1, 0)), # Exactly at end
        ((0.0, 0.0), (0, 0), (1, 0), 1.0, 0, 1500, (1.0, 0.0), (1, 0)), # Past end
        # Multiple cell moves
        ((0.0, 0.0), (0, 0), (5, 0), 1.0, 0, 2500, (2.5, 0.0), (2, 0)), # Halfway (2.5m)
        ((0.0, 0.0), (0, 0), (5, 0), 1.0, 0, 5000, (5.0, 0.0), (5, 0)), # At end
        # Diagonal movement (3-4-5 triangle)
        ((0.0, 0.0), (0, 0), (3, 4), 1.0, 0, 2500, (1.5, 2.0), (1, 2)), # Halfway point in m
        ((0.0, 0.0), (0, 0), (3, 4), 1.0, 0, 5000, (3.0, 4.0), (3, 4)), # At end point in m
        # Speed = 0 (infinite duration), should not move from initial position
        ((0.0, 0.0), (0, 0), (1, 0), 0.0, 0, 10000, (0.0, 0.0), (0, 0)), 
        # No start_time_ms set, should not move
        ((1.0, 1.0), (1, 1), (2, 2), 1.0, None, 100, (1.0, 1.0), (1, 1)),
    ])
    def test_move_physics_update_calculates_position_correctly(self, mock_board_physics, MockCommand_class,
                                                                 initial_pos_m, start_cell, end_cell, speed,
                                                                 start_time_ms, now_ms, expected_pos_m, expected_cell):
        """
        Arrange: Create MovePhysics object, set initial state and command for movement.
        Act: Call update with various 'now_ms' values.
        Assert: Verify cur_pos_m and get_cell() are updated correctly.
        """
        # Arrange
        move_obj = MovePhysics(start_cell=start_cell, board=mock_board_physics, speed_m_s=speed)
        move_obj.cur_pos_m = initial_pos_m # Set initial position directly for this test
        
        mock_cmd = MockCommand_class(timestamp=start_time_ms if start_time_ms is not None else 0, # provide dummy for init
                                     piece_id="p1", type="Move", params=list(end_cell))
        
        # Reset with the actual command only if start_time_ms is provided
        if start_time_ms is not None:
            move_obj.reset(mock_cmd)
        else: # For the case where start_time_ms is None (initial state)
            move_obj.cmd = mock_cmd # Set cmd without calling reset
            move_obj.start_time_ms = None # Ensure it stays None

        # Act
        returned_cmd = move_obj.update(now_ms=now_ms)

        # Assert
        assert returned_cmd is mock_cmd # Should always return the stored command

        # Using pytest.approx for float comparisons
        assert move_obj.cur_pos_m[0] == pytest.approx(expected_pos_m[0])
        assert move_obj.cur_pos_m[1] == pytest.approx(expected_pos_m[1])
        assert move_obj.get_cell() == expected_cell

        # Verify start_cell is updated to end_cell when movement completes
        if (start_time_ms is not None) and (now_ms - start_time_ms) / 1000.0 >= move_obj.duration_s:
            assert move_obj.start_cell == end_cell
        else:
            assert move_obj.start_cell == start_cell # Should remain initial if not finished


    def test_move_physics_can_be_captured_returns_false(self, mock_board_physics):
        """
        Arrange: Create MovePhysics object.
        Act: Call can_be_captured.
        Assert: Verify it returns False (as it's in motion).
        """
        # Arrange
        move_obj = MovePhysics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = move_obj.can_be_captured()

        # Assert
        assert result is False


    def test_move_physics_can_capture_returns_true(self, mock_board_physics):
        """
        Arrange: Create MovePhysics object.
        Act: Call can_capture.
        Assert: Verify it returns True (as it can capture at end of move).
        """
        # Arrange
        move_obj = MovePhysics(start_cell=(0, 0), board=mock_board_physics)

        # Act
        result = move_obj.can_capture()

        # Assert
        assert result is True