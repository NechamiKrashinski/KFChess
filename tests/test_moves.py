import pytest
from unittest.mock import MagicMock, patch
import pathlib
from typing import List, Tuple, Dict

# Import the class under test
from implementation.moves import Moves

class TestMoves:

    @pytest.fixture
    def mock_moves_txt_path(self):
        """Fixture for a mock pathlib.Path object."""
        return MagicMock(spec=pathlib.Path)

    @pytest.fixture
    def standard_dims(self):
        """Fixture for standard 8x8 chess board dimensions (rows, cols)."""
        return (8, 8)

    @pytest.fixture
    def moves_instance(self, mock_moves_txt_path, standard_dims):
        """Fixture for a Moves instance with standard board dimensions."""
        return Moves(moves_txt_path=mock_moves_txt_path, dims=standard_dims)

    # --- Test __init__ ---
    def test_moves_init_sanity_sets_attributes_correctly(self, mock_moves_txt_path, standard_dims):
        """
        Arrange: Provide mock path and dimensions.
        Act: Initialize Moves object.
        Assert: Verify dims and raw_moves are set correctly.
        """
        # Arrange (from fixtures)

        # Act
        moves = Moves(moves_txt_path=mock_moves_txt_path, dims=standard_dims)

        # Assert
        assert moves.dims == standard_dims
        assert moves.raw_moves == {} # _load_moves currently returns an empty dict

    # --- Test _load_moves (internal method) ---
    def test_moves_load_moves_returns_empty_dict_as_implemented(self, moves_instance, mock_moves_txt_path):
        """
        Arrange: Moves instance.
        Act: Call _load_moves.
        Assert: Verify it returns an empty dictionary as per current implementation.
        """
        # Arrange (from fixture)

        # Act
        loaded_moves = moves_instance._load_moves(mock_moves_txt_path)

        # Assert
        assert loaded_moves == {}


    # --- Test _is_straight_move (internal method) ---
    @pytest.mark.parametrize("dx, dy, expected", [
        (0, 1, True),    # Vertical
        (0, -1, True),   # Vertical
        (1, 0, True),    # Horizontal
        (-1, 0, True),   # Horizontal
        (1, 1, True),    # Diagonal
        (-1, -1, True),  # Diagonal
        (2, 2, True),    # Longer diagonal
        (-3, 3, True),   # Longer diagonal
        (1, 2, False),   # Knight-like move
        (2, 1, False),   # Knight-like move
        (0, 0, True),    # No move (considered straight)
        (3, 1, False),
    ])
    def test_is_straight_move(self, moves_instance, dx, dy, expected):
        """
        Arrange: Delta coordinates (dx, dy).
        Act: Call _is_straight_move.
        Assert: Verify if it correctly identifies straight/diagonal moves.
        """
        # Arrange (from @parametrize)

        # Act
        result = moves_instance._is_straight_move(dx, dy)

        # Assert
        assert result == expected

    # --- Test _is_path_blocked (internal method) ---
    @pytest.mark.parametrize("start_cell, end_cell, occupied_cells, expected_blocked", [
        ((0, 0), (0, 3), [], False), # Empty path
        ((0, 0), (0, 3), [(0, 1)], True), # Blocked by one cell
        ((0, 0), (0, 3), [(0, 2)], True), # Blocked by another cell
        ((0, 0), (0, 3), [(0, 0)], False), # Occupying start cell is not blocking
        ((0, 0), (0, 3), [(0, 3)], False), # Occupying end cell is not blocking
        ((0, 0), (0, 1), [], False), # One step move, no intermediate
        ((0, 0), (0, 0), [], False), # No move, no path
        ((0, 0), (2, 2), [(1, 1)], True), # Diagonal block
        ((0, 0), (3, 3), [(1, 1), (2, 2)], True), # Multiple blocks, first counts
        ((0, 0), (3, 3), [(1, 0)], False), # Not on path
        ((0, 0), (0, 7), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)], True), # Long path, many blocks
        ((0, 0), (7, 7), [(4, 4)], True), # Block on long diagonal
        ((0, 0), (7, 7), [], False), # Long diagonal, no block
        ((0, 0), (1, 0), [(1,0)], False) # End cell occupied (not a block)
    ])
    def test_is_path_blocked(self, moves_instance, start_cell, end_cell, occupied_cells, expected_blocked):
        """
        Arrange: Start, end cells, and a list of occupied cells.
        Act: Call _is_path_blocked.
        Assert: Verify if it correctly detects blockages on a straight path.
        """
        # Arrange (from @parametrize)

        # Act
        result = moves_instance._is_path_blocked(start_cell, end_cell, occupied_cells)

        # Assert
        assert result == expected_blocked

    # --- Test get_moves - Pawn (P) ---
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, my_color, expected_moves", [
        # White Pawn: Initial moves
        (0, 6, [], [], 'W', [(0, 5), (0, 4)]), # Start, empty board
        (0, 6, [(0, 5)], [], 'W', []), # Start, blocked 1 step
        # FIX START: Pawn cannot move straight to an occupied enemy cell, only capture diagonally.
        # This test case (0, 6, [(0, 5)], [(0, 5)], 'W', [(0, 4)]) implies a straight move to (0,5)
        # is allowed if it's an enemy, but it's not how pawns capture.
        # If (0,5) is an enemy, the pawn cannot move there directly. It needs to capture diagonally.
        # The (0,4) move is only possible if (0,5) is NOT occupied.
        # Assuming the pawn cannot move forward if the square in front is occupied, regardless if friendly or enemy.
        # And it can only capture diagonally.
        (0, 6, [(0, 5)], [(0, 5)], 'W', []), # Changed: Blocked by enemy in front, no straight move
        # FIX END
        (0, 6, [(0, 4)], [], 'W', [(0, 5)]), # Start, blocked 2 steps
        (0, 5, [], [], 'W', [(0, 4)]), # Not at start row, 1 step only
        # White Pawn: Captures
        (3, 4, [], [(2, 3)], 'W', [(3, 3), (2,3)]), # Capture left
        (3, 4, [], [(4, 3)], 'W', [(3, 3), (4,3)]), # Capture right
        (3, 4, [], [(2, 3), (4, 3)], 'W', [(3, 3), (2,3), (4,3)]), # Capture both
        (3, 4, [(3,3)], [(2,3)], 'W', [(2,3)]), # Blocked forward, can capture
        # White Pawn: Edge cases
        (0, 6, [], [(1, 5)], 'W', [(0, 5), (0, 4), (1, 5)]), # Edge, can capture right
        (7, 6, [], [(6, 5)], 'W', [(7, 5), (7, 4), (6, 5)]), # Edge, can capture left
        (0, 6, [(1,5)], [], 'W', [(0,5), (0,4)]), # No capture if square isn't enemy
        (0, 0, [], [], 'W', []), # At end of board
        # Black Pawn: Initial moves
        (0, 1, [], [], 'B', [(0, 2), (0, 3)]), # Start, empty board
        (0, 1, [(0, 2)], [], 'B', []), # Start, blocked 1 step
        (0, 1, [(0, 3)], [], 'B', [(0, 2)]), # Start, blocked 2 steps
        (0, 2, [], [], 'B', [(0, 3)]), # Not at start row, 1 step only
        # Black Pawn: Captures
        (3, 3, [], [(2, 4)], 'B', [(3, 4), (2,4)]), # Capture left
        (3, 3, [], [(4, 4)], 'B', [(3, 4), (4,4)]), # Capture right
        # Black Pawn: Edge cases
        (0, 1, [], [(1, 2)], 'B', [(0, 2), (0, 3), (1, 2)]), # Edge, can capture right
        (7, 1, [], [(6, 2)], 'B', [(7, 2), (7, 3), (6, 2)]), # Edge, can capture left
        (0, 7, [], [], 'B', []), # At end of board
    ])
    def test_get_moves_pawn(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, my_color, expected_moves):
        """
        Arrange: Piece position, board state for pawn.
        Act: Call get_moves for a pawn.         
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        # Ensure 'can_jump' is False for pawn     
        can_jump = False
        piece_type = 'P'

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves)


    # --- Test get_moves - Knight (N) ---
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, expected_moves", [
        # Knight: Empty board
        (3, 3, [], [], [(1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), # Center of board
        (0, 0, [], [], [(1, 2), (2, 1)]), # Corner
        (0, 1, [], [], [(2, 0), (2, 2), (1, 3)]), # Edge
        # Knight: Blocking by friendly
        (3, 3, [(1, 2)], [], [(1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), # One blocked by friendly
        (3, 3, [(1, 2), (1, 4)], [], [(2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), # Two blocked by friendly
        # Knight: Capturing enemy
        (3, 3, [(1, 2)], [(1, 2)], [(1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), # Capture one
        (3, 3, [(1, 2), (2, 1)], [(1, 2), (2, 1)], [(1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), # Capture two
        # Knight: Mixed (friendly block, enemy capture)
        (3, 3, [(1, 2), (2, 5)], [(1, 2)], [(1, 2), (1, 4), (2, 1), (4, 1), (4, 5), (5, 2), (5, 4)]),
        # Knight: All potential moves occupied by friendly (should be no moves)
        (3, 3, [ # Correctly define all knight target cells relative to (3,3)
            (1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)
        ], [], []), 
        # Knight: All potential moves occupied by enemy (should be all valid knight moves)
        (3, 3, [ # Correctly define all knight target cells relative to (3,3)
            (1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)
        ], [ # All occupied cells are enemy cells
            (1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)
        ], [(1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)]), 
    ])
    def test_get_moves_knight(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, expected_moves):
        """
        Arrange: Piece position, board state for knight.
        Act: Call get_moves for a knight.
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        # can_jump is True for knight
        can_jump = True 
        piece_type = 'N'
        my_color = 'W' # Color doesn't affect knight moves

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves)


    # --- Test get_moves - Rook (R) ---
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, expected_moves", [
        # Rook: Empty board (center)
        (3, 3, [], [], [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7), # Horizontal
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)  # Vertical
        ]),
        # Rook: Empty board (corner)
        (0, 0, [], [], [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), # Horizontal
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)  # Vertical
        ]),
        # Rook: Blocked by friendly piece
        (3, 3, [(3, 5)], [], [
            (3, 0), (3, 1), (3, 2), (3, 4), # Horiz R blocked
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)  # Vertical
        ]),
        (3, 3, [(1, 3)], [], [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7), # Horizontal
            (2, 3), (4, 3), (5, 3), (6, 3), (7, 3) # Vertical Up blocked
        ]),
        # Rook: Capturing enemy piece
        (3, 3, [(3, 5)], [(3, 5)], [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), # Capture at (3,5)
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)  # Vertical
        ]),
        (3, 3, [(1, 3)], [(1, 3)], [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7), # Horizontal
            (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3) # Capture at (1,3)
        ]),
        # Rook: Mixed (friendly block, enemy capture)
        (3, 3, [(3, 5), (1, 3)], [(3, 5)], [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), # Capture R at (3,5)
            (2, 3), (4, 3), (5, 3), (6, 3), (7, 3) # Vertical Up blocked by friendly at (1,3)
        ]),
        # Rook: Confined space
        (3, 3, [(2,3), (3,2), (4,3), (3,4)], [(2,3), (3,2), (4,3), (3,4)],
            [(2,3), (3,2), (4,3), (3,4)]), # Surrounded by enemies, can capture all
    ])
    def test_get_moves_rook(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, expected_moves):
        """
        Arrange: Piece position, board state for rook.
        Act: Call get_moves for a rook.
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        can_jump = False 
        piece_type = 'R'
        my_color = 'W' 

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves)


    # --- Test get_moves - Bishop (B) ---
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, expected_moves", [
        # Bishop: Empty board (center)
        (3, 3, [], [], [
            (0, 0), (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Diag 1 (up-left to down-right)
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0),          # Diag 2 (up-right to down-left)
        ]),
        # Bishop: Empty board (corner)
        (0, 0, [], [], [
            (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7) # Only one diagonal
        ]),
        # Bishop: Blocked by friendly piece
        (3, 3, [(1, 1)], [], [
            (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Diag 1 blocked up-left
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0) # Diag 2 unblocked
        ]),
        # Bishop: Capturing enemy piece
        (3, 3, [(1, 1)], [(1, 1)], [
            (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Capture at (1,1)
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)
        ]),
        # --- FIX START ---
        # Bishop: Mixed (friendly block, enemy capture)
        (3, 3, [(1, 1), (2, 4)], [(1, 1)], sorted([ 
            (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Capture (1,1)
            # (0, 6), (1, 5), # These were the problematic moves. (2,4) blocks this path.
            (4, 2), (5, 1), (6, 0) 
        ])),
        # --- FIX END ---
        # Bishop: Confined space
        (3, 3, [(2,2), (2,4), (4,2), (4,4)], [(2,2), (2,4), (4,2), (4,4)],
            [(2,2), (2,4), (4,2), (4,4)]), # Surrounded by enemies, can capture all
    ])
    def test_get_moves_bishop(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, expected_moves):
        """
        Arrange: Piece position, board state for bishop.
        Act: Call get_moves for a bishop.         
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        can_jump = False 
        piece_type = 'B'
        my_color = 'W' 

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves)


    # --- Test get_moves - Queen (Q) ---
    # Define a helper list for all possible Queen moves from (3,3) on an empty board
    # This avoids using r, c in the list literal directly within parametrize
    _queen_center_moves = sorted([
        (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7), # Horizontal
        (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3),  # Vertical
        (0, 0), (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Diag 1
        (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)           # Diag 2
    ])
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, expected_moves", [
        # Queen: Empty board (center) - combined Rook + Bishop
        (3, 3, [], [], _queen_center_moves),
        # Queen: Blocked by friendly piece
        (3, 3, [(3, 5), (1, 1)], [], sorted([
            (3, 0), (3, 1), (3, 2), (3, 4), # Horiz R blocked by (3,5)
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3),  # Vertical (no block)
            (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Diag 1 blocked up-left by (1,1)
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)            # Diag 2 (no block)
        ])),
        # Queen: Capturing enemy piece
        (3, 3, [(3, 5), (1, 1)], [(3, 5), (1, 1)], sorted([
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), # Capture at (3,5)
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3),  # Vertical
            (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7), # Capture at (1,1)
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)            # Diag 2 unblocked
        ])),
    ])
    def test_get_moves_queen(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, expected_moves):
        """
        Arrange: Piece position, board state for queen.
        Act: Call get_moves for a queen.
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        can_jump = False 
        piece_type = 'Q'
        my_color = 'W' 

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves) # Changed to sorted(expected_moves) for consistency and robustness

    # --- Test get_moves - King (K) ---
    @pytest.mark.parametrize("r, c, all_occupied_cells, occupied_enemy_cells, expected_moves", [
        # King: Empty board (center)
        (3, 3, [], [], [
            (2, 2), (2, 3), (2, 4),
            (3, 2),           (3, 4),
            (4, 2), (4, 3), (4, 4)
        ]),
        # King: Empty board (corner)
        (0, 0, [], [], [(0, 1), (1, 0), (1, 1)]),
        # King: Blocked by friendly
        (3, 3, [(2, 3)], [], [
            (2, 2), (2, 4),
            (3, 2),           (3, 4),
            (4, 2), (4, 3), (4, 4)
        ]),
        # King: Capturing enemy
        (3, 3, [(2, 3)], [(2, 3)], [
            (2, 2), (2, 3), (2, 4),
            (3, 2),           (3, 4),
            (4, 2), (4, 3), (4, 4)
        ]),
        # King: Surrounded by friendly (no moves)
        (3,3, [(2,2), (2,3), (2,4), (3,2), (3,4), (4,2), (4,3), (4,4)], [], []),
        # King: Surrounded by enemy (can capture all)
        (3,3, [(2,2), (2,3), (2,4), (3,2), (3,4), (4,2), (4,3), (4,4)], 
                    [(2,2), (2,3), (2,4), (3,2), (3,4), (4,2), (4,3), (4,4)], 
                    [(2,2), (2,3), (2,4), (3,2), (3,4), (4,2), (4,3), (4,4)]),
    ])
    def test_get_moves_king(self, moves_instance, r, c, all_occupied_cells, occupied_enemy_cells, expected_moves):
        """
        Arrange: Piece position, board state for king.
        Act: Call get_moves for a king.
        Assert: Verify the list of valid moves matches expected.
        """
        # Arrange (from @parametrize)
        can_jump = False 
        piece_type = 'K'
        my_color = 'W' 

        # Act
        actual_moves = moves_instance.get_moves(r, c, all_occupied_cells, occupied_enemy_cells, can_jump, piece_type, my_color)

        # Assert
        assert sorted(actual_moves) == sorted(expected_moves)