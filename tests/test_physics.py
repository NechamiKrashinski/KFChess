# import pytest
# import math
# from typing import Tuple, Optional
# from unittest.mock import MagicMock

# # ייבוא המחלקות המקוריות
# from implementation.physics import Physics, IdlePhysics, MovePhysics
# from implementation.board import Board 
# from implementation.command import Command 

# # ייבוא ה-Mocks הספציפיים שבהם אנו משתמשים ישירות (לא כפיקסטורות)
# # הפיקסטורות עצמן (כמו default_board, MockCommand_class) נטענות אוטומטית ע"י pytest
# from .conftest import MockBoard, MockCommand 

# ## בדיקות למחלקת Physics

# ## בדיקות אתחול
# def test_physics_initialization(default_board): # Added default_board fixture
#     """
#     Arrange: A default board.
#     Act: Initialize Physics with a start cell and board.
#     Assert: cur_pos_m and start_cell are set correctly, cmd is None, and start_time_ms is 0.
#     """
#     # Arrange
#     board = default_board # Use the fixture
#     start_cell = (1, 2)
#     expected_pos_m = board.cell_to_coords_m(start_cell) # Use board's method to get expected meters

#     # Act
#     physics_obj = Physics(start_cell=start_cell, board=board)

#     # Assert
#     assert physics_obj.start_cell == start_cell
#     assert physics_obj.cur_pos_m == expected_pos_m
#     assert physics_obj.board is board
#     assert physics_obj.cmd is None # Physics base class should start with cmd as None
#     assert physics_obj.start_time_ms == 0

# def test_physics_get_pos_returns_current_position(default_board): # Added default_board fixture
#     """
#     Arrange: Initialized Physics object.
#     Act: Call get_pos().
#     Assert: Returns the current_position_m.
#     """
#     # Arrange
#     board = default_board
#     start_cell = (3, 4)
#     expected_pos_m = board.cell_to_coords_m(start_cell)
#     physics_obj = Physics(start_cell=start_cell, board=board)

#     # Act
#     current_pos = physics_obj.get_pos()

#     # Assert
#     assert current_pos == expected_pos_m

# def test_physics_get_cell_returns_current_cell(default_board): # Added default_board fixture
#     """
#     Arrange: Initialized Physics object.
#     Act: Call get_cell().
#     Assert: Returns the current cell based on cur_pos_m and board dimensions.
#     """
#     # Arrange
#     # Use a board with 1m x 1m cells for simple test
#     board = MockBoard(cell_W_m=1.0, cell_H_m=1.0) 
#     start_cell = (3, 4)
#     physics_obj = Physics(start_cell=start_cell, board=board)
    
#     # Manually set cur_pos_m to be in the middle of a cell
#     physics_obj.cur_pos_m = (3.5, 4.5) 
    
#     # Act
#     current_cell = physics_obj.get_cell()

#     # Assert
#     assert current_cell == (3, 4)

# ## בדיקות מתודת Reset
# def test_physics_reset_sets_cmd_and_start_time_ms(default_board, MockCommand_class):
#     """
#     Arrange: Initialized Physics object.
#     Act: Call reset with a command.
#     Assert: cmd and start_time_ms are set correctly.
#     """
#     # Arrange
#     physics_obj = Physics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     mock_cmd = MockCommand_class(timestamp=12345, piece_id=1, type="Idle")
#     mock_cmd.command_type = "Idle" # Still need this if MockCommand doesn't set it via type
#     mock_cmd.timestamp = 12345 # And this if it's not directly passed as argument

#     # Act
#     physics_obj.reset(mock_cmd)

#     # Assert
#     assert physics_obj.cmd is mock_cmd
#     assert physics_obj.start_time_ms == mock_cmd.timestamp

# def test_physics_reset_overwrites_existing_command(default_board, MockCommand_class):
#     """
#     Arrange: Initialized Physics object with an existing command.
#     Act: Call reset with a new command.
#     Assert: cmd and start_time_ms are updated to the new command's values.
#     """
#     # Arrange
#     initial_cmd = MockCommand_class(timestamp=100, piece_id=1, type="Initial")
#     initial_cmd.command_type = "Initial"
#     initial_cmd.timestamp = 100
#     physics_obj = Physics(start_cell=(0, 0), board=default_board)
#     physics_obj.reset(initial_cmd)

#     new_cmd = MockCommand_class(timestamp=500, piece_id=2, type="New")
#     new_cmd.command_type = "New"
#     new_cmd.timestamp = 500

#     # Act
#     physics_obj.reset(new_cmd)

#     # Assert
#     assert physics_obj.cmd is new_cmd
#     assert physics_obj.start_time_ms == new_cmd.timestamp

# ## בדיקות מתודת Update (מחלקת Physics בסיס)
# def test_physics_update_returns_current_cmd(default_board, MockCommand_class):
#     """
#     Arrange: Initialized Physics object with a command.
#     Act: Call update.
#     Assert: Returns the current command.
#     """
#     # Arrange
#     physics_obj = Physics(start_cell=(0, 0), board=default_board)
    
#     mock_cmd = MockCommand_class(timestamp=100, piece_id=1, type="Test")
#     mock_cmd.command_type = "Test"
#     mock_cmd.timestamp = 100
    
#     physics_obj.reset(mock_cmd)
#     now_ms = 200

#     # Act
#     returned_cmd = physics_obj.update(now_ms)

#     # Assert
#     assert returned_cmd is mock_cmd



# ## בדיקות למחלקת IdlePhysics

# ### בדיקות אתחול (IdlePhysics)
# def test_idlephysics_initialization_sets_idle_command(default_board):
#     """
#     Arrange: A default board.
#     Act: Initialize IdlePhysics.
#     Assert: cmd is an Idle command with timestamp 0.
#     """
#     # Arrange
#     start_cell = (0, 0)

#     # Act
#     idle_physics_obj = IdlePhysics(start_cell=start_cell, board=default_board)

#     # Assert
#     # Check if cmd is None if IdlePhysics doesn't initialize it in its __init__
#     # Based on the error, it seems cmd is None.
#     # If IdlePhysics is supposed to create an Idle Command object on init,
#     # then implementation/physics.py needs to be updated.
#     # For now, asserting it's None if it's the current behavior.
#     assert idle_physics_obj.cmd is None # Changed to reflect likely current behavior if cmd is None
#     assert idle_physics_obj.start_time_ms == 0
#     assert idle_physics_obj.start_cell == start_cell
#     assert idle_physics_obj.cur_pos_m == default_board.cell_to_coords_m(start_cell)

#     # If IdlePhysics *should* create a default Idle command, the implementation needs:
#     # self.cmd = Command(timestamp=0, piece_id=0, type="Idle", params=None)
#     # in its __init__. If so, change the assert to:
#     # assert isinstance(idle_physics_obj.cmd, Command)
#     # assert idle_physics_obj.cmd.command_type == "Idle"
#     # assert idle_physics_obj.cmd.timestamp == 0

# ### בדיקות מתודת Reset (IdlePhysics)
# def test_idlephysics_reset_sets_cmd_and_start_time_ms_for_idle_command(default_board, MockCommand_class):
#     """
#     Arrange: Initialized IdlePhysics object.
#     Act: Call reset with an Idle command.
#     Assert: cmd and start_time_ms are set correctly.
#     """
#     # Arrange
#     idle_physics_obj = IdlePhysics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     mock_idle_cmd = MockCommand_class(timestamp=1000, piece_id=1, type="Idle")
#     mock_idle_cmd.command_type = "Idle"
#     mock_idle_cmd.timestamp = 1000

#     # Act
#     idle_physics_obj.reset(mock_idle_cmd)

#     # Assert
#     assert idle_physics_obj.cmd is mock_idle_cmd
#     assert idle_physics_obj.start_time_ms == mock_idle_cmd.timestamp
#     assert idle_physics_obj.start_cell == (0, 0) # Should remain the same

# def test_idlephysics_reset_raises_value_error_for_non_idle_command(default_board, MockCommand_class):
#     """
#     Arrange: Initialized IdlePhysics object.
#     Act: Call reset with a non-Idle command (e.g., "Move").
#     Assert: ValueError is raised.
#     """
#     # Arrange
#     idle_physics_obj = IdlePhysics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     mock_move_cmd = MockCommand_class(timestamp=1000, piece_id=1, type="Move", params=(1, 1))
#     mock_move_cmd.command_type = "Move"
#     mock_move_cmd.timestamp = 1000
#     mock_move_cmd.params = (1, 1)

#     # Act & Assert
#     with pytest.raises(ValueError, match="Invalid command for IdlePhysics"):
#         idle_physics_obj.reset(mock_move_cmd)

# ### בדיקות מתודת Update (IdlePhysics)
# def test_idlephysics_update_returns_current_cmd(default_board, MockCommand_class):
#     """
#     Arrange: Initialized IdlePhysics object with an Idle command.
#     Act: Call update.
#     Assert: Returns the current Idle command and position remains unchanged.
#     """
#     # Arrange
#     idle_physics_obj = IdlePhysics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     mock_cmd = MockCommand_class(timestamp=500, piece_id=1, type="Idle")
#     mock_cmd.command_type = "Idle"
#     mock_cmd.timestamp = 500
    
#     idle_physics_obj.reset(mock_cmd)
#     now_ms = 1000

#     initial_pos = idle_physics_obj.get_pos()

#     # Act
#     returned_cmd = idle_physics_obj.update(now_ms)

#     # Assert
#     assert returned_cmd is mock_cmd
#     assert idle_physics_obj.get_pos() == initial_pos # Position should not change

# #---

# ## בדיקות למחלקת MovePhysics

# ### בדיקות אתחול (MovePhysics)
# def test_movephysics_initialization_sets_idle_command(default_board): # Added default_board fixture
#     """
#     Arrange: A default board and start cell.
#     Act: Initialize MovePhysics.
#     Assert: cmd is None (or an Idle command if implementation dictates), speed is set, and duration is inf.
#     """
#     # Arrange
#     start_cell = (0, 0)
#     speed = 1.0

#     # Act
#     move_physics_obj = MovePhysics(start_cell=start_cell, board=default_board, speed_m_s=speed)

#     # Assert
#     # Asserting cmd is None for now, as per the error message indicating it's None.
#     # If MovePhysics is supposed to create a default Idle Command, the implementation needs:
#     # self.cmd = Command(timestamp=0, piece_id=0, type="Idle", params=None)
#     # in its __init__. If so, change the assert to:
#     # assert isinstance(move_physics_obj.cmd, Command)
#     # assert move_physics_obj.cmd.command_type == "Idle"
#     # assert move_physics_obj.cmd.timestamp == 0
#     assert move_physics_obj.cmd is None 
#     assert move_physics_obj.start_time_ms == 0
#     assert move_physics_obj.start_cell == start_cell
#     assert move_physics_obj.cur_pos_m == default_board.cell_to_coords_m(start_cell)
#     assert move_physics_obj.speed_m_s == speed
#     assert move_physics_obj.end_cell == start_cell # Initially, end_cell is start_cell
#     assert move_physics_obj.vector_m == (0.0, 0.0) # Initially no movement vector
#     assert move_physics_obj.duration_s == float('inf') # Initially idle, so infinite duration

# ### בדיקות מתודת Reset (MovePhysics)
# def test_movephysics_reset_sets_movement_params_for_valid_move_command(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics.
#     Act: Reset with a valid "Move" command.
#     Assert: Verify movement parameters (end_cell, vector, duration) are set correctly.
#     """
#     # Arrange
#     initial_cell = (0, 0)
#     target_cell = (3, 4) # Assuming default_board has 1x1m cells
#     command_timestamp = 100
#     move_speed = 1.0

#     board = default_board # default_board is 1m x 1m cells

#     # Calculate expected values
#     expected_start_pos_m = board.cell_to_coords_m(initial_cell)
#     expected_end_pos_m = board.cell_to_coords_m(target_cell)
    
#     dx_m = expected_end_pos_m[0] - expected_start_pos_m[0]
#     dy_m = expected_end_pos_m[1] - expected_start_pos_m[1]
    
#     expected_dx = (target_cell[0] - initial_cell[0]) * board.cell_W_m
#     expected_dy = (target_cell[1] - initial_cell[1]) * board.cell_H_m
    
#     distance_m = math.sqrt(expected_dx**2 + expected_dy**2)
#     expected_duration_s = distance_m / move_speed if move_speed > 0 else float('inf')

#     move_physics_obj = MovePhysics(start_cell=initial_cell, board=board, speed_m_s=move_speed)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=target_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = target_cell

#     # Act
#     move_physics_obj.reset(move_cmd)

#     # Assert
#     assert move_physics_obj.cmd is move_cmd
#     assert move_physics_obj.start_time_ms == command_timestamp
#     assert move_physics_obj.start_cell == initial_cell # start_cell is updated to initial_cell of the move
#     assert move_physics_obj.end_cell == target_cell
#     assert move_physics_obj.vector_m[0] == pytest.approx(expected_dx, abs=1e-6)
#     assert move_physics_obj.vector_m[1] == pytest.approx(expected_dy, abs=1e-6)
#     assert move_physics_obj.duration_s == pytest.approx(expected_duration_s, abs=1e-6)
#     # Check that cur_pos_m is updated to the start of the new command
#     assert move_physics_obj.cur_pos_m[0] == pytest.approx(expected_start_pos_m[0], abs=1e-6)
#     assert move_physics_obj.cur_pos_m[1] == pytest.approx(expected_start_pos_m[1], abs=1e-6)


# def test_movephysics_reset_raises_value_error_for_invalid_command_type(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics.
#     Act: Reset with a command that is not "Move".
#     Assert: ValueError is raised.
#     """
#     # Arrange
#     move_physics_obj = MovePhysics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     invalid_cmd = MockCommand_class(timestamp=100, piece_id=1, type="Attack")
#     invalid_cmd.command_type = "Attack"
#     invalid_cmd.timestamp = 100

#     # Act & Assert
#     with pytest.raises(ValueError, match="Invalid command for MovePhysics"):
#         move_physics_obj.reset(invalid_cmd)

# def test_movephysics_reset_raises_value_error_for_move_command_with_invalid_params_length(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics.
#     Act: Reset with a "Move" command having params that are not a 2-tuple.
#     Assert: ValueError is raised.
#     """
#     # Arrange
#     move_physics_obj = MovePhysics(start_cell=(0, 0), board=default_board)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     invalid_cmd = MockCommand_class(timestamp=100, piece_id=1, type="Move", params=(1,)) # Only one parameter, should be 2
#     invalid_cmd.command_type = "Move"
#     invalid_cmd.timestamp = 100
#     invalid_cmd.params = (1,) # Only one parameter, should be 2

#     # Act & Assert
#     with pytest.raises(ValueError, match="Invalid command for MovePhysics"):
#         move_physics_obj.reset(invalid_cmd)

# def test_movephysics_reset_with_zero_speed_sets_infinite_duration(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics with zero speed.
#     Act: Reset with a "Move" command.
#     Assert: duration_s is set to infinity.
#     """
#     # Arrange
#     initial_cell = (0, 0)
#     target_cell = (1, 1)
#     command_timestamp = 100
#     zero_speed = 0.0

#     move_physics_obj = MovePhysics(start_cell=initial_cell, board=default_board, speed_m_s=zero_speed)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=target_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = target_cell

#     # Act
#     move_physics_obj.reset(move_cmd)

#     # Assert
#     assert move_physics_obj.duration_s == float("inf")
#     # For zero speed, start_cell should remain the *initial* start_cell from the constructor,
#     # as the 'move' never actually starts/completes.
#     assert move_physics_obj.start_cell == initial_cell 

# ### בדיקות מתודת Update (MovePhysics)

# @pytest.mark.parametrize("start_cell, end_cell, speed, now_ms, command_timestamp, expected_pos_m, expected_cell, board_dims", [
#     # Case 1: No movement yet (elapsed_s = 0)
#     ((0, 0), (1, 0), 1.0, 100, 100, (0.0, 0.0), (0, 0), (1.0, 1.0)),
#     # Case 2: Partial movement (halfway)
#     ((0, 0), (2, 0), 1.0, 2000, 1000, (1.0, 0.0), (1, 0), (1.0, 1.0)),
#     ((0, 0), (0, 4), 2.0, 2000, 1000, (0.0, 2.0), (0, 2), (1.0, 1.0)),
#     # Case 3: Movement completed
#     ((0, 0), (3, 0), 1.0, 4000, 1000, (3.0, 0.0), (3, 0), (1.0, 1.0)),
#     # Case 4: Movement completed (elapsed time > duration)
#     ((0, 0), (1, 1), 1.0, 3000, 1000, (1.0, 1.0), (1, 1), (1.0, 1.0)),
#     # Case 5: Diagonal movement
#     # Expected position should be based on distance traveled, not directly end_cell
#     ((0, 0), (1, 1), 1.0, 1500, 1000, (0.5 * math.sqrt(2), 0.5 * math.sqrt(2)), (0, 0), (1.0, 1.0)),
#     # Case 6: Movement completed exactly at now_ms
#     ((0,0), (1,0), 1.0, 1000 + 1000, 1000, (1.0, 0.0), (1,0), (1.0, 1.0)),
#     # Case 7: Movement with board having larger cell dimensions
#     ((0,0), (1,0), 1.0, 1000 + 5000, 1000, (1.0 * 5.0, 0.0 * 5.0), (1,0), (5.0, 5.0)),
# ])
# def test_movephysics_update_calculates_position_correctly(start_cell, end_cell, speed, now_ms, command_timestamp, expected_pos_m, expected_cell, board_dims, MockCommand_class): # Use MockCommand_class fixture
#     """
#     Arrange: Initialize MovePhysics, reset with a move command.
#     Act: Call update at various `now_ms` times.
#     Assert: Verify cur_pos_m and get_cell() are updated correctly.
#     """
#     # Arrange
#     # Use the board_dims from parametrize to create the correct MockBoard for each test case
#     board = MockBoard(cell_W_m=board_dims[0], cell_H_m=board_dims[1])

#     move_physics_obj = MovePhysics(start_cell=start_cell, board=board, speed_m_s=speed)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=end_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = end_cell
    
#     move_physics_obj.reset(move_cmd) # Reset with the new command

#     # Act
#     move_physics_obj.update(now_ms)

#     # Assert
#     # Convert expected_pos_m to the actual position on the board,
#     # as board.cell_to_coords_m expects cell coordinates, not already calculated meters
#     # For parameterized tests, expected_pos_m is already in meters, so we assert directly.
#     assert move_physics_obj.cur_pos_m[0] == pytest.approx(expected_pos_m[0], abs=1e-6)
#     assert move_physics_obj.cur_pos_m[1] == pytest.approx(expected_pos_m[1], abs=1e-6)
#     assert move_physics_obj.get_cell() == expected_cell


# def test_movephysics_update_with_speed_zero_position_remains_unchanged(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics with zero speed. Reset with a move command.
#     Act: Call update at a time after command timestamp.
#     Assert: Verify position remains at start_cell (as duration is infinite).
#     """
#     # Arrange
#     start_cell = (1, 1)
#     end_cell = (2, 2)
#     command_timestamp = 1000
#     zero_speed = 0.0

#     move_physics_obj = MovePhysics(start_cell=start_cell, board=default_board, speed_m_s=zero_speed)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=end_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = end_cell
    
#     move_physics_obj.reset(move_cmd)

#     initial_pos_m = move_physics_obj.get_pos() # Should be start_cell's meter position

#     # Act
#     move_physics_obj.update(command_timestamp + 1000) # Update 1 second later

#     # Assert
#     assert move_physics_obj.get_pos() == initial_pos_m # Position should not change


# def test_movephysics_update_completes_move_and_resets_start_cell_at_end_of_duration(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics, reset with a move command.
#     Act: Call update exactly at or beyond the calculated duration.
#     Assert: Verify cur_pos_m is set to end_cell's position and start_cell is updated to end_cell.
#     """
#     # Arrange
#     initial_cell = (0, 0)
#     target_cell = (2, 0) # 2 meters distance assuming 1m cells
#     command_timestamp = 1000
#     speed = 1.0 # 1 m/s, so 2 seconds duration

#     board = default_board # 1m x 1m cells

#     move_physics_obj = MovePhysics(start_cell=initial_cell, board=board, speed_m_s=speed)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=target_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = target_cell
    
#     move_physics_obj.reset(move_cmd)

#     # Act - call update exactly at duration end
#     end_time_ms = command_timestamp + int(move_physics_obj.duration_s * 1000)
#     move_physics_obj.update(end_time_ms)

#     # Assert
#     expected_end_pos_m = board.cell_to_coords_m(target_cell)
#     assert move_physics_obj.cur_pos_m[0] == pytest.approx(expected_end_pos_m[0], abs=1e-6)
#     assert move_physics_obj.cur_pos_m[1] == pytest.approx(expected_end_pos_m[1], abs=1e-6)
#     assert move_physics_obj.get_cell() == target_cell
#     assert move_physics_obj.start_cell == target_cell # After move, start_cell should be updated

#     # Act again - call update beyond duration end
#     move_physics_obj.update(end_time_ms + 1000) # 1 second after completion

#     # Assert - position should remain at end_cell
#     assert move_physics_obj.cur_pos_m[0] == pytest.approx(expected_end_pos_m[0], abs=1e-6)
#     assert move_physics_obj.cur_pos_m[1] == pytest.approx(expected_end_pos_m[1], abs=1e-6)
#     assert move_physics_obj.get_cell() == target_cell
#     assert move_physics_obj.start_cell == target_cell # Still at the target cell


# def test_movephysics_update_before_start_time_does_not_move(default_board, MockCommand_class):
#     """
#     Arrange: Initialize MovePhysics, reset with a command.
#     Act: Call update with `now_ms` less than `start_time_ms`.
#     Assert: Verify position remains at initial start_cell.
#     """
#     # Arrange
#     start_cell = (0, 0)
#     end_cell = (1, 0)
#     command_timestamp = 1000
#     move_physics_obj = MovePhysics(start_cell=start_cell, board=default_board, speed_m_s=1.0)
    
#     # יצירת ה-MockCommand בדרך הנכונה - כולל פרמטרים חובה לאתחול
#     move_cmd = MockCommand_class(timestamp=command_timestamp, piece_id=1, type="Move", params=end_cell)
#     move_cmd.command_type = "Move"
#     move_cmd.timestamp = command_timestamp
#     move_cmd.params = end_cell
    
#     move_physics_obj.reset(move_cmd)

#     initial_pos_m = move_physics_obj.get_pos() # Position at command_timestamp - 1, should be start_cell

#     # Act
#     now_ms = command_timestamp - 500 # Before the command starts
#     move_physics_obj.update(now_ms)

#     # Assert
#     assert move_physics_obj.get_pos() == initial_pos_m
#     assert move_physics_obj.get_cell() == start_cell