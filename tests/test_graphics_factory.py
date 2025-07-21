import pytest
import tempfile
import shutil
import pathlib
import numpy as np
import cv2

from implementation.graphics_factory import GraphicsFactory
from implementation.graphics import Graphics


@pytest.fixture
def temp_sprite_dir():
    """Create a temporary sprite folder structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)

        # Create PB with 2 states: idle and move
        for piece_id in ["PB", "QW"]:
            for state in ["idle", "move"]:
                sprite_path = root / piece_id / "states" / state / "sprites"
                sprite_path.mkdir(parents=True, exist_ok=True)
                for i in range(2):  # 2 frames per state
                    img = np.ones((64, 64, 3), dtype=np.uint8) * (100 + i)
                    file_path = sprite_path / f"{i}.png"
                    cv2.imwrite(str(file_path), img)

        yield root


@pytest.fixture
def dummy_board():
    class DummyBoard:
        cell_H_pix = 64
        cell_W_pix = 64
    return DummyBoard()


def test_load_valid_graphics(temp_sprite_dir, dummy_board):
    gf = GraphicsFactory()
    cfg = {"PB": True, "QW": True}

    result = gf.load(temp_sprite_dir, cfg, dummy_board)

    assert isinstance(result, dict)
    assert "PB" in result
    assert "QW" in result
    assert "idle" in result["PB"]
    assert "move" in result["PB"]

    for piece_id in cfg:
        for state in ["idle", "move"]:
            g = result[piece_id][state]
            assert isinstance(g, Graphics)
            assert len(g.sprites) == 2
            assert g.sprites[0].img.shape == (64, 64, 3)


def test_missing_states_folder(temp_sprite_dir, dummy_board):
    # Remove folder for QW
    shutil.rmtree(temp_sprite_dir / "QW")

    gf = GraphicsFactory()
    cfg = {"PB": True, "QW": True}

    with pytest.raises(FileNotFoundError, match="Missing states folder for QW"):
        gf.load(temp_sprite_dir, cfg, dummy_board)


def test_empty_state_sprites(temp_sprite_dir, dummy_board):
    # Remove sprite images from one state
    sprite_dir = temp_sprite_dir / "PB" / "states" / "move" / "sprites"
    for f in sprite_dir.iterdir():
        f.unlink()

    gf = GraphicsFactory()
    cfg = {"PB": True}

    result = gf.load(temp_sprite_dir, cfg, dummy_board)

    assert "move" not in result["PB"]
    assert "idle" in result["PB"]


def test_no_valid_states(temp_sprite_dir, dummy_board):
    # Remove all sprite files for PB
    pb_dir = temp_sprite_dir / "PB"
    shutil.rmtree(pb_dir)

    gf = GraphicsFactory()
    cfg = {"PB": True}

    with pytest.raises(FileNotFoundError, match="Missing states folder for PB"):
        gf.load(temp_sprite_dir, cfg, dummy_board)


def test_empty_config(temp_sprite_dir, dummy_board):
    gf = GraphicsFactory()
    cfg = {}

    result = gf.load(temp_sprite_dir, cfg, dummy_board)
    assert result == {}


def test_loop_and_fps_values(temp_sprite_dir, dummy_board):
    gf = GraphicsFactory()
    cfg = {"PB": True}
    result = gf.load(temp_sprite_dir, cfg, dummy_board, loop=False, fps=10.0)

    g = result["PB"]["idle"]
    assert g.loop is False
    assert g.fps == 10.0
