from .board import Board
from .mock_img import MockImg


class MockBoard(Board):
    """
    A mock implementation of the Board class for testing Graphics.
    Initializes with dummy pixel dimensions and a MockImg instance.
    """
    def __init__(self, cell_W_pix: int = 50, cell_H_pix: int = 50):
        super().__init__(
            cell_H_pix=cell_H_pix,
            cell_W_pix=cell_W_pix,
            cell_H_m=1,
            cell_W_m=1,
            W_cells=10,
            H_cells=10,
            img=MockImg() # MockBoard should also use MockImg internally
        )
        # אין צורך להגדיר internal_state אם לא משתמשים בו!

    def copy(self) -> 'MockBoard':
        """
        יוצרת עותק של MockBoard.
        """
        new_board = MockBoard(
            cell_W_pix=self.cell_W_pix,
            cell_H_pix=self.cell_H_pix
        )
        # הסר את השורה הזו אם אין internal_state אמיתי ב-MockBoard
        # new_board.internal_state = self.internal_state 
        return new_board


    def clone(self) -> 'MockBoard':
        """
        Mocks the clone operation, returning a new MockBoard instance.
        """
        return MockBoard(cell_W_pix=self.cell_W_pix, cell_H_pix=self.cell_H_pix)
