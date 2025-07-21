import pytest
import numpy as np
from unittest.mock import MagicMock
from implementation.board import Board
from implementation.command import Command
from implementation.state import State
from implementation.mock_img import MockImg


@pytest.fixture(autouse=True)
def reset_mockimg():
    """מאפס את ההיסטוריה של MockImg לפני כל טסט"""
    MockImg.reset()
    yield


@pytest.fixture
def dummy_board():
    img = MockImg()
    return Board(
        cell_H_pix=100,
        cell_W_pix=100,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
        img=img
    )


@pytest.fixture
def dummy_state():
    state = MagicMock(spec=State)

    dummy_cmd = Command(
        timestamp=0,
        piece_id='P1',
        type='Move',
        params=[(0, 0), (1, 1)]
    )

    state.get_command.return_value = dummy_cmd
    state.can_transition.return_value = True
    state.process_command.return_value = state
    state.update.return_value = state

    # גרפיקה
    img = MockImg()
    state._graphics = MagicMock()
    state._graphics.get_img.return_value = img

    # פיזיקה
    state._physics = MagicMock()
    state._physics.get_pos.return_value = (1.0, 1.0)

    return state
