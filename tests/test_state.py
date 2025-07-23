# import pytest
# from implementation.state import State
# from implementation.command import Command
# from implementation.graphics import Graphics
# from implementation.physics import Physics
# from implementation.moves import Moves
# from unittest.mock import MagicMock


# @pytest.fixture
# def fake_deps():
#     moves = MagicMock(spec=Moves)
#     graphics = MagicMock(spec=Graphics)
#     physics = MagicMock(spec=Physics)
#     return moves, graphics, physics


# def test_initialization_stores_deps_and_empty_transitions(fake_deps):
#     moves, graphics, physics = fake_deps
#     state = State(moves, graphics, physics)
#     assert state._graphics == graphics
#     assert state._physics == physics
#     assert state._moves == moves
#     assert isinstance(state._transitions, dict)
#     assert len(state._transitions) == 0
#     assert state.get_command() is None


# def test_set_transition_and_overwrite(fake_deps):
#     moves, graphics, physics = fake_deps
#     s = State(moves, graphics, physics)
#     s1 = State(moves, graphics, physics)
#     s2 = State(moves, graphics, physics)

#     s.set_transition("Move", s1)
#     assert s._transitions["Move"] == s1

#     # Overwrite existing transition
#     s.set_transition("Move", s2)
#     assert s._transitions["Move"] == s2


# def test_reset_sets_command_and_resets_subsystems(fake_deps):
#     moves, graphics, physics = fake_deps
#     state = State(moves, graphics, physics)
#     cmd = Command(timestamp=123, piece_id="p1", type="Move", params=["a2", "a3"])

#     state.reset(cmd)

#     assert state.get_command() == cmd
#     graphics.reset.assert_called_once()
#     physics.reset.assert_called_once()


# def test_update_no_command_returns_self(fake_deps):
#     moves, graphics, physics = fake_deps
#     graphics.update.return_value = None
#     physics.update.return_value = None

#     state = State(moves, graphics, physics)
#     returned = state.update(1000)
#     assert returned == state
#     graphics.update.assert_called_once_with(1000)
#     physics.update.assert_called_once_with(1000)


# def test_update_with_command_triggers_process_command(fake_deps):
#     moves, graphics, physics = fake_deps
#     cmd = Command(timestamp=1000, piece_id="p2", type="Jump", params=["high"])

#     graphics.update.return_value = None
#     physics.update.return_value = cmd

#     state = State(moves, graphics, physics)
#     s2 = MagicMock(spec=State)
#     state.set_transition("Jump", s2)

#     next_state = state.update(1000)

#     assert next_state == s2
#     s2.reset.assert_called_once_with(cmd)


# def test_process_command_no_transition_returns_self(fake_deps):
#     moves, graphics, physics = fake_deps
#     state = State(moves, graphics, physics)
#     cmd = Command(timestamp=100, piece_id="p3", type="Fly", params=[])

#     result = state.process_command(cmd, 100)
#     assert result == state
#     assert state.get_command() == cmd


# def test_process_command_with_valid_transition(fake_deps):
#     moves, graphics, physics = fake_deps
#     state1 = State(moves, graphics, physics)
#     state2 = MagicMock(spec=State)
#     state1.set_transition("Move", state2)
#     cmd = Command(timestamp=200, piece_id="p4", type="Move", params=["e2", "e4"])

#     next_state = state1.process_command(cmd, 200)

#     assert next_state == state2
#     state2.reset.assert_called_once_with(cmd)
#     assert state1.get_command() == cmd


# def test_can_transition_returns_true_by_default(fake_deps):
#     moves, graphics, physics = fake_deps
#     state = State(moves, graphics, physics)
#     assert state.can_transition(0) is True
#     assert state.can_transition(100000) is True


# def test_get_command_returns_none_if_not_set(fake_deps):
#     moves, graphics, physics = fake_deps
#     state = State(moves, graphics, physics)
#     assert state.get_command() is None
