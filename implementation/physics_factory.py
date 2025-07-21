from .board import Board
from .physics import Physics


class PhysicsFactory:
    """
    Factory responsible for creating Physics objects for pieces on the board.
    """

    def __init__(self, board: Board):
        """
        Initialize with a reference to the board to map logical positions to physical ones.

        Parameters
        ----------
        board : Board
            The board object used to calculate physical positions.
        """
        self.board = board

    def create(self, start_cell: tuple[int, int], cfg: dict) -> Physics:
        """
        Create a Physics object based on initial cell position and configuration.

        Parameters
        ----------
        start_cell : (col, row)
            The starting position of the piece on the board.
        cfg : dict
            Optional configuration dictionary for physics parameters.

        Returns
        -------
        Physics
            A Physics object positioned at the physical coordinates of the given cell.
        """
        if not isinstance(start_cell, tuple) or len(start_cell) != 2:
            raise ValueError("start_cell must be a (col, row) tuple")

        col, row = start_cell
        if not (0 <= col < self.board.W_cells and 0 <= row < self.board.H_cells):
            raise ValueError(f"start_cell {start_cell} out of board bounds")

        # Get speed from config, default to 1.0 if not provided
        speed = cfg.get("speed", 1.0)

        # Create the Physics object using the original constructor
        physics = Physics(start_cell=start_cell, board=self.board, speed_m_s=speed)

        return physics
