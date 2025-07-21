from .board import Board
from .physics import Physics, IdlePhysics, MovePhysics
from typing import Tuple

class PhysicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def create(self, start_cell: Tuple[int, int], cfg: dict) -> Physics:
        """
        Create a physics object based on the given configuration.
        """
        physics_cfg = cfg.get("physics", {})
        speed_m_s = physics_cfg.get("speed_m_per_sec", 0.0)
        
        # יוצר אובייקט Physics מתאים בהתבסס על מהירות
        if speed_m_s > 0:
            return MovePhysics(start_cell=start_cell, board=self.board, speed_m_s=speed_m_s)
        else:
            return IdlePhysics(start_cell=start_cell, board=self.board)