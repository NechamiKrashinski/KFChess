# utils.py

def to_chess_notation(row: int, col: int) -> str:
    file = chr(ord('a') + col)
    rank = str(8 - row)
    return f"{file}{rank}"
