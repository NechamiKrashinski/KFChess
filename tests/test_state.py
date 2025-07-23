# tests/test_state.py
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Optional, Tuple

# ייבוא המחלקות המקוריות הנבדקות
from implementation.command import Command
from implementation.moves import Moves
from implementation.graphics import Graphics
from implementation.physics import Physics, MovePhysics
from implementation.state import State

# ייבוא MockCommand מ-conftest.py
from .conftest import MockCommand_class

class TestState:

    @pytest.fixture
    def mock_dependencies(self):
        """
        Fixture to create mock objects for Graphics, Physics, and Moves.
        These mocks will be used in tests for the State class.
        """
        mock_graphics = MagicMock(spec=Graphics)
        mock_physics = MagicMock(spec=Physics)
        mock_moves = MagicMock(spec=Moves)
        return mock_graphics, mock_physics, mock_moves

    @pytest.fixture
    def initial_state(self, mock_dependencies):
        """
        Fixture to create an initial State object for tests.
        """
        mock_graphics, mock_physics, mock_moves = mock_dependencies
        return State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics)
    
    @pytest.fixture
    def mock_command_idle(self, MockCommand_class):
        return MockCommand_class(timestamp=100, piece_id="p1", type="Idle", params=[])

    @pytest.fixture
    def mock_command_move(self, MockCommand_class):
        return MockCommand_class(timestamp=200, piece_id="p1", type="Move", params=[(1, 2)])

    @pytest.fixture
    def mock_command_capture(self, MockCommand_class):
        return MockCommand_class(timestamp=300, piece_id="p1", type="Capture", params=[])

    # --- Test __init__ ---
    def test_state_init_sanity_sets_attributes_correctly(self, mock_dependencies):
        """
        Arrange: Provide mock dependencies.
        Act: Initialize State object.
        Assert: Verify all internal attributes are set to the provided dependencies and default values.
        """
        # Arrange
        mock_graphics, mock_physics, mock_moves = mock_dependencies

        # Act
        state = State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics)

        # Assert
        assert state._graphics is mock_graphics
        assert state._physics is mock_physics
        assert state._moves is mock_moves
        assert state._transitions == {}
        assert state._current_command is None

    # --- Test set_transition ---
    def test_state_set_transition_adds_transition_correctly(self, initial_state):
        """
        Arrange: Initial State object and a target State.
        Act: Call set_transition.
        Assert: Verify the transition is stored in _transitions.
        """
        # Arrange
        mock_graphics, mock_physics, mock_moves = MagicMock(spec=Graphics), MagicMock(spec=Physics), MagicMock(spec=Moves)
        target_state = State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics)

        # Act
        initial_state.set_transition(event="Idle", target=target_state)

        # Assert
        assert initial_state._transitions["Idle"] is target_state
        assert len(initial_state._transitions) == 1

    def test_state_set_transition_overwrites_existing_transition(self, initial_state):
        """
        Arrange: Initial State object with an existing transition and a new target State.
        Act: Call set_transition with the same event.
        Assert: Verify the transition is overwritten.
        """
        # Arrange
        mock_graphics, mock_physics, mock_moves = MagicMock(spec=Graphics), MagicMock(spec=Physics), MagicMock(spec=Moves)
        old_target_state = State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics)
        new_target_state = State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics)

        initial_state.set_transition(event="Idle", target=old_target_state)

        # Act
        initial_state.set_transition(event="Idle", target=new_target_state)

        # Assert
        assert initial_state._transitions["Idle"] is new_target_state
        assert len(initial_state._transitions) == 1 # Still only one entry

    # --- Test reset ---
    def test_state_reset_updates_command_and_resets_dependencies(self, initial_state, mock_command_idle):
        """
        Arrange: Initial State object and a mock Command.
        Act: Call reset.
        Assert: Verify _current_command is set, and reset methods of graphics/physics are called.
        """
        # Arrange
        state = initial_state
        mock_graphics = state._graphics
        mock_physics = state._physics

        # Act
        state.reset(mock_command_idle)

        # Assert
        assert state._current_command is mock_command_idle
        mock_graphics.reset.assert_called_once_with(cmd=mock_command_idle)
        mock_physics.reset.assert_called_once_with(cmd=mock_command_idle)

    # --- Test update ---
    def test_state_update_calls_graphics_update(self, initial_state):
        """
        Arrange: Initial State object.
        Act: Call update.
        Assert: Verify graphics.update is called.
        """
        # Arrange
        state = initial_state
        mock_graphics = state._graphics
        mock_physics = state._physics # Need physics mock to return something

        # Act
        state.update(now_ms=100)

        # Assert
        mock_graphics.update.assert_called_once_with(100)
        # physics.update is also called, but we don't assert its return value here

    def test_state_update_returns_self_if_physics_update_returns_none(self, initial_state):
        """
        Arrange: Initial State where physics.update returns None.
        Act: Call update.
        Assert: Verify the same State object is returned.
        """
        # Arrange
        state = initial_state
        state._physics.update.return_value = None # Simulate no command from physics

        # Act
        result_state = state.update(now_ms=100)

        # Assert
        assert result_state is state
        state._graphics.update.assert_called_once_with(100)
        state._physics.update.assert_called_once_with(100)

    def test_state_update_calls_process_command_if_physics_update_returns_command(self, initial_state, mock_command_idle):
        """
        Arrange: Initial State where physics.update returns a Command.
        Act: Call update.
        Assert: Verify process_command is called with the returned command.
        """
        # Arrange
        state = initial_state
        state._physics.update.return_value = mock_command_idle # Simulate physics returning a command
        
        # We need to mock process_command to check if it's called
        with patch.object(state, 'process_command', return_value=state) as mock_process_command:
            # Act
            result_state = state.update(now_ms=100)

            # Assert
            mock_process_command.assert_called_once_with(mock_command_idle, 100)
            assert result_state is state # Assuming process_command returns self for this mock

    # --- Test process_command ---
    def test_state_process_command_updates_current_command(self, initial_state, mock_command_idle):
        """
        Arrange: Initial State and a mock Command.
        Act: Call process_command.
        Assert: Verify _current_command is updated.
        """
        # Arrange
        state = initial_state

        # Act
        # For this test, we don't care about the return value or side effects of transitions,
        # just that the command is stored. We'll handle different command types in other tests.
        state.process_command(mock_command_idle, now_ms=100) 

        # Assert
        assert state._current_command is mock_command_idle


    @patch('implementation.state.State', autospec=True) # Mock the State class itself
    @patch('implementation.physics.MovePhysics', autospec=True) # Mock MovePhysics class
    def test_state_process_command_move_creates_new_move_state(self, MockMovePhysics, MockState_class, initial_state, mock_command_move):
        """
        Arrange: Initial State, mock Command 'Move', and mock MovePhysics/State classes.
        Act: Call process_command with 'Move' command.
        Assert: Verify new MovePhysics created, new State created, new State reset, and new State returned.
        """
        # Arrange
        state = initial_state
        
        # Configure physics mock to return a mock MovePhysics instance
        mock_new_physics_instance = MagicMock(spec=MovePhysics)
        state._physics.create_movement_to.return_value = mock_new_physics_instance

        # Configure MockState_class to return a mock new_state instance
        mock_new_state_instance = MagicMock(spec=State)
        MockState_class.return_value = mock_new_state_instance

        # Act
        returned_state = state.process_command(mock_command_move, now_ms=mock_command_move.timestamp)

        # Assert
        # 1. Physics.create_movement_to was called with correct parameters
        state._physics.create_movement_to.assert_called_once_with(tuple(mock_command_move.params))
        
        # 2. A new State object was created with the new physics
        MockState_class.assert_called_once_with(
            moves=state._moves,
            graphics=state._graphics,
            physics=mock_new_physics_instance
        )
        
        # 3. The new state's reset method was called
        mock_new_state_instance.reset.assert_called_once_with(mock_command_move)
        
        # 4. The new state object was returned
        assert returned_state is mock_new_state_instance


    def test_state_process_command_known_transition_returns_target_state_and_resets_it(self, initial_state, mock_command_idle):
        """
        Arrange: Initial State with a defined transition for 'Idle' command.
        Act: Call process_command with 'Idle' command.
        Assert: Verify the target State is returned and its reset method is called.
        """
        # Arrange
        state = initial_state
        
        # Create a mock target state and set it as a transition
        mock_target_state = MagicMock(spec=State)
        state.set_transition("Idle", mock_target_state)

        # Act
        returned_state = state.process_command(mock_command_idle, now_ms=mock_command_idle.timestamp)

        # Assert
        assert returned_state is mock_target_state
        mock_target_state.reset.assert_called_once_with(mock_command_idle)
        assert state._current_command is mock_command_idle # Still updates current command

    def test_state_process_command_unknown_transition_returns_self(self, initial_state, mock_command_capture):
        """
        Arrange: Initial State without a defined transition for 'Capture' command.
        Act: Call process_command with 'Capture' command.
        Assert: Verify the current State object is returned unchanged.
        """
        # Arrange
        state = initial_state
        # Ensure no transition for "Capture"
        assert "Capture" not in state._transitions

        # Act
        returned_state = state.process_command(mock_command_capture, now_ms=mock_command_capture.timestamp)

        # Assert
        assert returned_state is state
        # Ensure no calls to reset on any theoretical next_state
        assert state._graphics.reset.call_count == 0 
        assert state._physics.reset.call_count == 0 
        assert state._current_command is mock_command_capture # Still updates current command

    # --- Test can_transition ---
    def test_state_can_transition_always_returns_true(self, initial_state):
        """
        Arrange: Initial State.
        Act: Call can_transition.
        Assert: Verify it returns True.
        """
        # Arrange
        state = initial_state

        # Act
        result = state.can_transition(now_ms=100)

        # Assert
        assert result is True

    # --- Test getters ---
    def test_state_get_command_returns_current_command(self, initial_state, mock_command_idle):
        """
        Arrange: Initial State with _current_command set.
        Act: Call get_command.
        Assert: Verify the correct command is returned.
        """
        # Arrange
        state = initial_state
        state._current_command = mock_command_idle

        # Act
        command = state.get_command()

        # Assert
        assert command is mock_command_idle

    def test_state_get_command_returns_none_when_no_command_set(self, initial_state):
        """
        Arrange: Initial State with no command set.
        Act: Call get_command.
        Assert: Verify None is returned.
        """
        # Arrange
        state = initial_state
        state._current_command = None

        # Act
        command = state.get_command()

        # Assert
        assert command is None


    def test_state_get_graphics_returns_graphics_object(self, initial_state, mock_dependencies):
        """
        Arrange: Initial State.
        Act: Call get_graphics.
        Assert: Verify the correct graphics mock object is returned.
        """
        # Arrange
        state = initial_state
        mock_graphics, _, _ = mock_dependencies

        # Act
        graphics_obj = state.get_graphics()

        # Assert
        assert graphics_obj is mock_graphics


    def test_state_get_physics_returns_physics_object(self, initial_state, mock_dependencies):
        """
        Arrange: Initial State.
        Act: Call get_physics.
        Assert: Verify the correct physics mock object is returned.
        """
        # Arrange
        state = initial_state
        _, mock_physics, _ = mock_dependencies

        # Act
        physics_obj = state.get_physics()

        # Assert
        assert physics_obj is mock_physics


    def test_state_get_moves_returns_moves_object(self, initial_state, mock_dependencies):
        """
        Arrange: Initial State.
        Act: Call get_moves.
        Assert: Verify the correct moves mock object is returned.
        """
        # Arrange
        state = initial_state
        _, _, mock_moves = mock_dependencies

        # Act
        moves_obj = state.get_moves()

        # Assert
        assert moves_obj is mock_moves