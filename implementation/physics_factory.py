from .board import Board
from .physics import JumpPhysics, Physics, IdlePhysics, MovePhysics
from typing import Tuple

class PhysicsFactory:
    def __init__(self, board: Board):
        self.board = board
        

    def create(self, start_cell: Tuple[int, int], cfg: dict, state: str = "idle") -> Physics:
        """Create a physics object based on the given configuration."""
        physics_cfg = cfg.get("physics", {})
        speed_m_s = physics_cfg.get("speed_m_per_sec", 0.0)
        next_state_name = physics_cfg.get("next_state_when_finished", "idle")
 
        if state == "move":
            # אם המצב הוא תנועה, ניצור אובייקט MovePhysics
           return MovePhysics(
            start_cell=start_cell,
            board=self.board,
            speed_m_s=speed_m_s,
            next_state_name=next_state_name
        )
        if state == "jump":
            return JumpPhysics(
                start_cell=start_cell,
                board=self.board,
                speed_m_s=speed_m_s,
                next_state_name=next_state_name
            )
        else:
            return IdlePhysics(start_cell=start_cell, board=self.board)
