import pytest
from unittest.mock import MagicMock, patch
from implementation.command import Command
from implementation.moves import Moves
from implementation.graphics import Graphics
from implementation.physics import Physics
from implementation.state import State

class TestState:

    @pytest.fixture
    def mock_dependencies(self):
        mock_graphics = MagicMock(spec=Graphics)
        mock_physics = MagicMock(spec=Physics)
        mock_moves = MagicMock(spec=Moves)
        return mock_graphics, mock_physics, mock_moves

    @pytest.fixture
    def initial_state(self, mock_dependencies):
        mock_graphics, mock_physics, mock_moves = mock_dependencies
        return State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics, state="idle")

    @pytest.fixture
    def mock_command_idle(self):
        return Command(timestamp=100, piece_id="p1", type="Idle", params=[])

    @pytest.fixture
    def mock_command_move(self):
        return Command(timestamp=200, piece_id="p1", type="Move", params=[(1, 2)])

    @pytest.fixture
    def mock_command_capture(self):
        return Command(timestamp=300, piece_id="p1", type="Capture", params=[])

    def test_init_sets_all_attributes_correctly(self, mock_dependencies):
        mock_graphics, mock_physics, mock_moves = mock_dependencies
        state = State(moves=mock_moves, graphics=mock_graphics, physics=mock_physics, state="idle")
        assert state._graphics is mock_graphics
        assert state._physics is mock_physics
        assert state._moves is mock_moves
        assert isinstance(state._transitions, dict)
        assert state._transitions == {}
        assert state._current_command is None
        assert state._current_state == "idle"

    def test_set_transition_adds_and_overwrites(self, initial_state, mock_dependencies):
        mock_graphics, mock_physics, mock_moves = mock_dependencies
        target1 = State(mock_moves, mock_graphics, mock_physics, state="state1")
        target2 = State(mock_moves, mock_graphics, mock_physics, state="state2")
        initial_state.set_transition("event1", target1)
        initial_state.set_transition("event1", target2)
        assert initial_state._transitions["event1"] is target2
        assert len(initial_state._transitions) == 1

    def test_reset_updates_current_command_and_resets_dependencies(self, initial_state, mock_command_idle):
        state = initial_state
        state.reset(mock_command_idle)
        assert state._current_command is mock_command_idle
        state._graphics.reset.assert_called_once_with(cmd=mock_command_idle)
        state._physics.reset.assert_called_once_with(cmd=mock_command_idle)

    def test_update_calls_graphics_and_physics_update_and_returns_self_when_no_command(self, initial_state):
        state = initial_state
        state._physics.update.return_value = None
        state._graphics.loop = False
        state._graphics.is_finished.return_value = False

        result = state.update(now_ms=123)

        state._graphics.update.assert_called_once_with(123)
        state._physics.update.assert_called_once_with(123)
        assert result is state

    def test_update_calls_process_command_when_physics_emits_command(self, initial_state, mock_command_idle):
        state = initial_state
        state._physics.update.return_value = mock_command_idle
        with patch.object(state, "process_command", return_value=state) as mock_proc_cmd:
            result = state.update(now_ms=50)
            mock_proc_cmd.assert_called_once_with(mock_command_idle, 50)
            assert result is state

    def test_update_emits_finished_rest_command_when_graphics_finished_and_not_looping(self, initial_state, mock_command_idle):
        state = initial_state
        state._current_command = mock_command_idle
        state._graphics.loop = False
        state._graphics.is_finished.return_value = True
        state._physics.update.return_value = None

        with patch.object(state, "process_command", return_value=state) as mock_proc_cmd:
            result = state.update(now_ms=500)
            assert mock_proc_cmd.call_count == 1
            call_args = mock_proc_cmd.call_args[0]
            cmd_arg = call_args[0]
            now_ms_arg = call_args[1]

            assert cmd_arg.type == "finished_rest"
            assert cmd_arg.piece_id == mock_command_idle.piece_id
            assert now_ms_arg == 500
            assert result is state

    def test_process_command_with_known_transition_resets_and_returns_target_state(self, initial_state, mock_command_idle):
        state = initial_state
        target_state = State(state._moves, state._graphics, state._physics, state="target")
        state.set_transition("Idle", target_state)

        state._physics.get_pos.return_value = (10, 20)
        state._physics.get_cell.return_value = (5, 5)

        target_state.reset = MagicMock()

        returned = state.process_command(mock_command_idle, now_ms=mock_command_idle.timestamp)

        assert returned is target_state
        target_state.reset.assert_called_once_with(mock_command_idle)
        assert target_state.get_physics().cur_pos_m == (10, 20)
        assert target_state.get_physics().start_cell == (5, 5)
        assert state._current_command is mock_command_idle

    def test_process_command_with_unknown_transition_returns_self_and_updates_command(self, initial_state, mock_command_capture):
        state = initial_state
        assert "Capture" not in state._transitions

        returned = state.process_command(mock_command_capture, now_ms=mock_command_capture.timestamp)

        assert returned is state
        assert state._current_command is mock_command_capture

    def test_can_transition_always_returns_true(self, initial_state):
        state = initial_state
        result = state.can_transition(now_ms=1000)
        assert result is True

    def test_getters_return_expected_attributes(self, initial_state, mock_dependencies, mock_command_idle):
        state = initial_state
        mock_graphics, mock_physics, mock_moves = mock_dependencies
        state._current_command = mock_command_idle

        assert state.get_command() is mock_command_idle
        assert state.get_graphics() is mock_graphics
        assert state.get_physics() is mock_physics
        assert state.get_moves() is mock_moves
        assert state.get_state() == "idle"