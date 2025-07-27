import pytest
from unittest.mock import MagicMock, patch
import cv2
import numpy as np

# Assuming these are in the same parent directory for relative import
# You might need to adjust the import paths based on your actual project structure
# For testing purposes, we'll mock them extensively.
from implementation.physics import Physics
from implementation.piece import Piece
from implementation.board import Board
from implementation.command import Command
from implementation.state import State # Make sure State is imported
from implementation.moves import Moves

# Mock dependencies as they are external or have complex internal logic
# We only care that Piece interacts with them correctly.

class TestPiece:

    @pytest.fixture
    def mock_initial_state(self):
        """Fixture for a mock initial State object."""
        return State()

    @pytest.fixture
    def piece_id(self):
        """Fixture for a sample piece ID."""
        return "PWB1" # Pawn White Bishop 1, example ID

    @pytest.fixture
    def piece_instance(self, piece_id, mock_initial_state):
        """Fixture for a Piece instance."""
        return Piece(piece_id, mock_initial_state)

    # --- Test __init__ ---
    def test_init_sets_piece_id_and_state_correctly(self, piece_id, mock_initial_state):
        """
        Arrange: Provide a piece ID and an initial State mock.
        Act: Initialize Piece object.
        Assert: Verify piece_id and _state attributes are set correctly,
                and _last_command_time is initialized to 0.
        """
        # Arrange (from fixtures)

        # Act
        piece = Piece(piece_id, mock_initial_state)

        # Assert
        assert piece.piece_id == piece_id
        assert piece._state == mock_initial_state
        assert piece._last_command_time == 0

    # --- Test on_command ---
    @pytest.mark.parametrize("can_transition_return_val, expected_state_change, expected_last_command_time_update", [
        (True, True, True),   # Command possible, state should change, time should update
        (False, False, False) # Command not possible, state should not change, time should not update
    ])
    def test_on_command_processes_command_when_possible(self, piece_instance, mock_initial_state, can_transition_return_val,
                                                         expected_state_change, expected_last_command_time_update):
        """
        Arrange: Piece instance, mock command, and control can_transition behavior.
        Act: Call on_command.
        Assert: Verify if process_command on state is called and _last_command_time is updated based on can_transition.
        """
        # Arrange
        cmd = Command(timestamp=1000, piece_id=piece_instance.piece_id, type="move", params=[])
        now_ms = 1000
        
        # Configure the mock_initial_state to control can_transition behavior
        mock_initial_state._can_transition_val = can_transition_return_val
        
        # Mock the return value of process_command to be a *new* mock state
        new_mock_state = State(can_transition_val=can_transition_return_val)
        # We need to ensure that the process_command method of the MockState returns the new state
        mock_initial_state._process_command_return_state = new_mock_state # Set internal value

        initial_state_before_command = piece_instance._state # Capture initial state for comparison

        # Act
        piece_instance.on_command(cmd, now_ms)

        # Assert
        if expected_state_change:
            # Check if process_command was called on the *original* state object
            mock_initial_state.process_command.assert_called_once_with(cmd, now_ms)
            # Verify the piece's internal state was updated to the new state returned by process_command
            assert piece_instance._state == new_mock_state
            assert piece_instance._last_command_time == now_ms
        else:
            mock_initial_state.process_command.assert_not_called()
            # State should remain the same if command was not possible
            assert piece_instance._state == initial_state_before_command
            assert piece_instance._last_command_time == 0 # Should remain initial value

    def test_on_command_does_not_process_if_can_transition_false(self, piece_instance, mock_initial_state):
        """
        Arrange: Piece instance where state.can_transition returns False.
        Act: Call on_command.
        Assert: Verify process_command is NOT called and _last_command_time is NOT updated.
        """
        # Arrange
        cmd = Command(timestamp=1000, piece_id=piece_instance.piece_id, type="move", params=[])
        now_ms = 1000
        mock_initial_state._can_transition_val = False # Set internal value
        initial_last_command_time = piece_instance._last_command_time # Should be 0 initially

        # Act
        piece_instance.on_command(cmd, now_ms)

        # Assert
        mock_initial_state.process_command.assert_not_called()
        assert piece_instance._last_command_time == initial_last_command_time


    # --- Test is_command_possible ---
    @pytest.mark.parametrize("can_transition_return_val, expected_result", [
        (True, True),
        (False, False)
    ])
    def test_is_command_possible_delegates_to_state_can_transition(self, piece_instance, mock_initial_state,
                                                                   can_transition_return_val, expected_result):
        """
        Arrange: Piece instance, control state.can_transition return value.
        Act: Call is_command_possible.
        Assert: Verify it correctly returns the value from state.can_transition and calls it.
        """
        # Arrange
        now_ms = 500
        mock_initial_state._can_transition_val = can_transition_return_val # Set internal value

        # Act
        result = piece_instance.is_command_possible(Command(timestamp=1000, piece_id=piece_instance.piece_id, type="move", params=[]), now_ms)

        # Assert
        assert result == expected_result
        mock_initial_state.can_transition.assert_called_once_with(now_ms)

    # --- Test reset ---
    @pytest.mark.parametrize("command_exists", [True, False])
    def test_reset_updates_last_command_time_and_resets_state_if_command_exists(self, piece_instance, mock_initial_state, command_exists):
        """
        Arrange: Piece instance, a start_ms, and a state that may or may not return a command.
        Act: Call reset.
        Assert: Verify _last_command_time is updated, and state.reset is called conditionally.
        """
        # Arrange
        start_ms = 200
        mock_cmd = Command(timestamp=1000, piece_id=piece_instance.piece_id, type="move", params=[]) if command_exists else None

        mock_initial_state._command = mock_cmd # Set internal value for get_command

        # Act
        piece_instance.reset(start_ms)

        # Assert
        assert piece_instance._last_command_time == start_ms
        mock_initial_state.get_command.assert_called_once()
        if command_exists:
            mock_initial_state.reset.assert_called_once_with(mock_cmd)
        else:
            mock_initial_state.reset.assert_not_called()

    # --- Test update ---
    def test_update_delegates_to_state_update(self, piece_instance, mock_initial_state):
        """
        Arrange: Piece instance.
        Act: Call update.
        Assert: Verify state.update is called and internal state is updated with the returned state.
        """
        # Arrange
        now_ms = 300
        new_state_after_update = State() # Simulate a new state object returned by update
        mock_initial_state._update_return_state = new_state_after_update # Set internal value

        # Act
        piece_instance.update(now_ms)

        # Assert
        mock_initial_state.update.assert_called_once_with(now_ms)
        assert piece_instance._state == new_state_after_update 

    # --- Test draw_on_board ---
    
    @patch('cv2.rectangle') # Patch cv2.rectangle as it's a global function
    def test_draw_on_board_draws_piece_and_cooldown_if_not_possible(self, mock_rectangle, piece_instance, mock_initial_state):
        """
        Arrange: Piece instance, mock board, and control state.can_transition.
        Act: Call draw_on_board.
        Assert: Verify graphics methods are called for drawing and cooldown (conditionally).
        """
        # Arrange - תרחיש 1
        mock_board = Board()    
        mock_board.cell_W_m = 0.1
        mock_board.cell_H_m = 0.1
        mock_board.cell_W_pix = 100
        mock_board.cell_H_pix = 100
        mock_board.W_cells = 8
        mock_board.H_cells = 8
        mock_board.img = np.zeros((800, 800, 3), dtype=np.uint8) # תמונת לוח מדומה         
 
        now_ms = 400

        mock_graphics_obj = mock_initial_state.get_graphics() # גישה למוק הפנימי
        mock_physics_obj = mock_initial_state.get_physics() # **הוספה: גישה למוק הפיזיקה**

        # הגדר את מיקום הכלי עבור תרחיש 1
        mock_physics_obj.get_pos.return_value = (0.3, 0.2) # מיקום לדוגמה במטרים (r=3, c=2)
        
        # תרחיש 1: יכול לעבור (אין קירור)
        mock_initial_state._can_transition_val = True # הגדרת ערך פנימי

        # Act 1
        piece_instance.draw_on_board(mock_board, now_ms)

        # Assert 1
        mock_initial_state.update.assert_called_once_with(now_ms)     
        mock_graphics_obj.get_img.assert_called_once()
        
        # צפוי draw_x = 0.3 / 0.1 * 100 = 300
        # צפוי draw_y = 0.2 / 0.1 * 100 = 200
        mock_graphics_obj.get_img.return_value.draw_on.assert_called_once_with(other_img=mock_board.img, x=300, y=200)
        mock_graphics_obj.clone.assert_not_called() # אין קירור
        mock_rectangle.assert_not_called()     

        # איפוס מוקים עבור תרחיש 2
        mock_initial_state.reset_internal_mocks() 
        mock_rectangle.reset_mock()
        # **הוספה: איפוס מוק הפיזיקה וקביעת מיקום חדש עבור תרחיש 2**
        mock_physics_obj.reset_mock() 
        mock_physics_obj.get_pos.return_value = (0.3, 0.2) # קביעה מחדש גם עבור תרחיש זה, אם נשאר באותו מיקום או אחר

        # תרחיש 2: לא יכול לעבור (יש קירור)
        mock_initial_state._can_transition_val = False # הגדרת ערך פנימי

        # Act 2
        piece_instance.draw_on_board(mock_board, now_ms)

        # Assert 2
        # update() נקרא פעם אחת לכל "Act"
        mock_initial_state.update.assert_called_once_with(now_ms)
        # get_img() נקרא פעם אחת לכל "Act"
        mock_graphics_obj.get_img.assert_called_once()
        
        # draw_on על האובייקט שהוחזר מ-get_img() נקרא פעם אחת (הכלי עצמו)
        mock_graphics_obj.get_img.return_value.draw_on.assert_called_once_with(other_img=mock_board.img, x=300, y=200)

        mock_graphics_obj.clone.assert_called_once() # אמור לשכפל עבור קירור
        # הקריאה ל-cv2.rectangle צריכה להיות על ה-img של האובייקט המשוכפל
        mock_rectangle.assert_called_once_with(mock_graphics_obj.clone.return_value.img, (0, 0), (50, 50), (0, 0, 255), -1)
        
        # draw_on על האובייקט שהוחזר מ-clone() נקרא פעם אחת (שכבת הקירור)
        mock_graphics_obj.clone.return_value.draw_on.assert_called_once_with(
            other_img=mock_board.img, x=300, y=200, alpha=0.4
        )
        
    @patch('builtins.print') # Patch builtins.print to check warnings
    def test_draw_on_board_handles_piece_off_board_positions(self, mock_print, piece_instance, mock_initial_state):
        """
        Arrange: Piece positioned outside board boundaries.
        Act: Call draw_on_board.
        Assert: Verify drawing coordinates are clamped to board boundaries and warning is printed.
        """
        # Arrange
        mock_board = Board()
        mock_board.cell_W_m = 0.1
        mock_board.cell_H_m = 0.1
        mock_board.cell_W_pix = 100
        mock_board.cell_H_pix = 100
        mock_board.W_cells = 8
        mock_board.H_cells = 8
        mock_board.img = np.zeros((800, 800, 3), dtype=np.uint8)      

        now_ms = 400

        mock_graphics_obj = mock_initial_state.get_graphics()       

        mock_physics_obj = mock_initial_state.get_physics()
        mock_initial_state._can_transition_val = True # Set internal value # No cooldown for this test

        # Test case 1: Piece too far left/up (negative coordinates)
        mock_physics_obj.get_pos.return_value = (-0.5, -0.5) # Equivalent to (-5, -5) in cells
        
        # Act
        piece_instance.draw_on_board(mock_board, now_ms)
        
        # Assert
        mock_graphics_obj.get_img.return_value.draw_on.assert_called_once_with(other_img=mock_board.img, x=0, y=0)
        mock_print.assert_called_with(f"Warning: Piece drawing for {piece_instance.piece_id} at (-500, -500) exceeds board dimensions.")
        
        # Reset mocks for next test case
        mock_graphics_obj.reset_mock()
        mock_print.reset_mock()
        mock_initial_state.update.reset_mock() # Reset update calls for next scenario


        # Test case 2: Piece too far right/down (exceeds board)
        # Board width = 800px, height = 800px. Piece 50x50. Max draw_x = 750, max draw_y = 750
        mock_physics_obj.get_pos.return_value = (0.78, 0.78) # Equivalent to (7.8, 7.8) in cells
        
        # Act
        piece_instance.draw_on_board(mock_board, now_ms)

        # Assert
        mock_graphics_obj.get_img.return_value.draw_on.assert_called_once_with(other_img=mock_board.img, x=750, y=750) # Clamped to (800-50, 800-50)
        mock_print.assert_called_with(f"Warning: Piece drawing for {piece_instance.piece_id} at (780, 780) exceeds board dimensions.")


    # --- Test get_physics ---
    def test_get_physics_returns_state_physics(self, piece_instance, mock_initial_state):
        """
        Arrange: Piece instance.
        Act: Call get_physics.
        Assert: Verify it returns the physics object from the internal state.
        """
        # Arrange (from fixtures)

        # Act
        physics_obj = piece_instance.get_physics()

        # Assert
        # Corrected: Access the internal physics mock directly
        assert physics_obj == mock_initial_state._physics_mock 

    # --- Test get_moves ---
    @pytest.mark.parametrize("piece_id, expected_can_jump", [
        ("NW1", True),   # Knight
        ("PW2", False), # Pawn
        ("QB1", False), # Queen
        ("RW3", False), # Rook
        ("BW4", False), # Bishop
        ("KB5", False), # King
        ("nB1", True)   # lowercase knight
    ])
    def test_get_moves_calculates_correct_parameters_and_delegates_to_moves_logic(self, piece_id, expected_can_jump):
        """
        Arrange: Piece with specific ID, list of other pieces (some friendly, some enemy).
        Act: Call get_moves.
        Assert: Verify the parameters passed to moves_logic.get_moves are correct.
        """
        # Arrange
        # Initialize mock_state correctly to ensure its internal mocks are set up
        mock_state = State(initial_cell=(3, 3)) # Piece itself is at (3,3)
        piece_instance = Piece(piece_id, mock_state)

        # Create mock 'other' pieces
        # Assuming piece_id format: TypeColorNumber (e.g., PWB1, NW2)
        my_color = piece_id[1].upper()
        
        # Define some other pieces and their cells
        mock_other_pieces = [
            Piece( piece_id=f"X{my_color}1"), # Friendly piece
            Piece( piece_id=f"Y{'B' if my_color == 'W' else 'W'}1"), # Enemy piece
            Piece( piece_id=f"Z{my_color}2"), # Another friendly piece
        ]
        # Set return values on the *internal physics mock* of each piece
        for mock_p in mock_other_pieces:
            mock_p.get_physics.return_value = Physics()
            mock_p.get_physics.return_value.get_cell = Physics().get_cell

        mock_other_pieces[0].get_physics.return_value.get_cell.return_value = (1, 1) # Friendly
        mock_other_pieces[1].get_physics.return_value.get_cell.return_value = (2, 2) # Enemy
        mock_other_pieces[2].get_physics.return_value.get_cell.return_value = (4, 4) # Friendly

        all_pieces = [piece_instance] + mock_other_pieces

        expected_all_occupied_cells = [(1, 1), (2, 2), (4, 4)]
        expected_occupied_enemy_cells = [(2, 2)]
        expected_piece_type_char = piece_id[0].upper()
        
        # Configure the mock moves_logic to return a dummy list
        # Corrected: Access the internal moves mock directly
        mock_moves_logic = mock_state._moves_mock 
        mock_moves_logic.get_moves.return_value = [(0, 0), (1, 1)] # Dummy return value

        # Act
        actual_valid_moves = piece_instance.get_moves(all_pieces)

        # Assert
        mock_moves_logic.get_moves.assert_called_once_with(
            r=3,
            c=3,
            all_occupied_cells=expected_all_occupied_cells,
            occupied_enemy_cells=expected_occupied_enemy_cells,
            can_jump=expected_can_jump,
            piece_type=expected_piece_type_char,
            my_color=my_color
        )
        assert actual_valid_moves == [(0, 0), (1, 1)] # Ensure the returned value is passed through

    def test_get_moves_handles_no_other_pieces(self, piece_instance, mock_initial_state):
        """
        Arrange: Piece instance with no other pieces on the board.
        Act: Call get_moves.
        Assert: Verify empty lists are passed for occupied cells.
        """
        # Arrange
        # Corrected: Set return value on the internal physics mock
        mock_initial_state._physics_mock.get_cell.return_value = (3, 3)
        
        # Corrected: Access the internal moves mock directly
        mock_moves_logic = mock_initial_state._moves_mock
        mock_moves_logic.get_moves.return_value = [(0, 0)] # Dummy return

        all_pieces = [piece_instance] # Only this piece on the board

        # Act
        piece_instance.get_moves(all_pieces)

        # Assert
        mock_moves_logic.get_moves.assert_called_once_with(
            r=3,
            c=3,
            all_occupied_cells=[], # Should be empty
            occupied_enemy_cells=[], # Should be empty
            can_jump=False, # Assuming default piece_id leads to False (e.g., "PWB1")
            piece_type='P',
            my_color='W'
        )

    def test_get_moves_handles_all_other_pieces_friendly(self, piece_id):
        """
        Arrange: Piece instance and all other pieces are friendly.
        Act: Call get_moves.
        Assert: Verify occupied_enemy_cells is empty.
        """
        # Arrange
        mock_state = State(initial_cell=(3, 3))
        piece_instance = Piece(piece_id, mock_state)
        my_color = piece_id[1].upper()

        mock_other_pieces = [
            Piece(piece_id=f"X{my_color}1"),
            Piece(piece_id=f"Y{my_color}2"),
        ]
        # Set return values on the *internal physics mock* of each piece
        for mock_p in mock_other_pieces:
            mock_p.get_physics.return_value = Physics()
            mock_p.get_physics.return_value.get_cell = Physics().get_cell

        mock_other_pieces[0].get_physics.return_value.get_cell.return_value = (1, 1)
        mock_other_pieces[1].get_physics.return_value.get_cell.return_value = (2, 2)

        all_pieces = [piece_instance] + mock_other_pieces
        expected_all_occupied_cells = [(1, 1), (2, 2)]

        # Corrected: Access the internal moves mock directly
        mock_moves_logic = mock_state._moves_mock
        mock_moves_logic.get_moves.return_value = []

        # Act
        piece_instance.get_moves(all_pieces)

        # Assert
        mock_moves_logic.get_moves.assert_called_once_with(
            r=3,
            c=3,
            all_occupied_cells=expected_all_occupied_cells,
            occupied_enemy_cells=[], # Should be empty
            can_jump=False if piece_id[0].upper() != 'N' else True,
            piece_type=piece_id[0].upper(),
            my_color=my_color
        )