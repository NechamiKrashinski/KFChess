import pytest
from pathlib import Path
from implementation.moves import Moves  # שנה אם המיקום של הקובץ אחר

# רשימת כל כלי השחמט (שחור ולבן)
PIECES = [
    "BB", "BW",  # Bishop Black, Bishop White
    "RB", "RW",  # Rook Black, Rook White
    "NB", "NW",  # Knight Black, Knight White
    "QB", "QW",  # Queen Black, Queen White
    "KB", "KW",  # King Black, King White
    "PB", "PW"   # Pawn Black, Pawn White
]


BOARD_SIZE = (8, 8)

# מיקומים לבדיקה
TEST_POSITIONS = {
    "corner_top_left": (0, 0),
    "corner_top_right": (0, 7),
    "corner_bottom_left": (7, 0),
    "corner_bottom_right": (7, 7),
    "center": (3, 3),
    "edge_top": (0, 3),
    "edge_bottom": (7, 4),
    "edge_left": (4, 0),
    "edge_right": (3, 7),
}

# נתיב מוחלט אל התיקייה המכילה את כל הקבצים
BASE_RESOURCES_PATH = Path(r"C:\Users\user1\Documents\Bootcamp\KFChess\pieces_resources")


@pytest.mark.parametrize("piece_id", PIECES)
@pytest.mark.parametrize("pos_name", TEST_POSITIONS.keys())
def test_moves_within_board_bounds(piece_id, pos_name):
    moves_path = BASE_RESOURCES_PATH / piece_id / "moves.txt"
    print(f"[TEST DEBUG] Checking file: {moves_path.resolve()} (exists? {moves_path.exists()})")
    moves_obj = Moves(moves_path, BOARD_SIZE)
    r, c = TEST_POSITIONS[pos_name]
    valid_moves = moves_obj.get_moves(r, c)

    for nr, nc in valid_moves:
        assert 0 <= nr < BOARD_SIZE[0], f"Row out of bounds for {piece_id} at pos {r,c}"
        assert 0 <= nc < BOARD_SIZE[1], f"Col out of bounds for {piece_id} at pos {r,c}"

    for dx, dy in moves_obj.move_offsets:
        nr = r + dx
        nc = c + dy
        if 0 <= nr < BOARD_SIZE[0] and 0 <= nc < BOARD_SIZE[1]:
            assert (nr, nc) in valid_moves, f"Missing move {(nr,nc)} for {piece_id} at pos {r,c}"


@pytest.mark.parametrize("piece_id", PIECES)
def test_invalid_move_file_raises(piece_id, tmp_path):
    folder = tmp_path / piece_id
    folder.mkdir()
    file_path = folder / "moves.txt"
    file_path.write_text("a,b\n1,2\n3")
    with pytest.raises(ValueError):
        Moves(file_path, BOARD_SIZE)


@pytest.mark.parametrize("piece_id", PIECES)
def test_empty_move_file_results_in_no_moves(piece_id, tmp_path):
    folder = tmp_path / piece_id
    folder.mkdir()
    file_path = folder / "moves.txt"
    file_path.write_text("")
    moves_obj = Moves(file_path, BOARD_SIZE)
    assert moves_obj.move_offsets == []
    assert moves_obj.get_moves(4, 4) == []
