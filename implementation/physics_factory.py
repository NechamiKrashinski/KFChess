# physics_factory.py
from typing import Tuple
from .board import Board
from .physics import Physics, IdlePhysics, MovePhysics

class PhysicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def create(self, start_cell: Tuple[int, int], cfg: dict) -> Physics: 
        """
        Creates a physics object based on the given configuration.
        """
        physics_cfg = cfg.get("physics", {})
        
        # Determine physics type based on 'type' key in config, defaulting to IdlePhysics
        physics_type = physics_cfg.get("type", "IdlePhysics")
        
        # Common parameters that might be used by different physics types
        speed_m_s = physics_cfg.get("speed_m_per_sec", 0.0) # Used for movement
        # next_state_when_finished should be passed to the specific physics object
        next_state_name = physics_cfg.get("next_state_when_finished") 

        if physics_type == "MovePhysics":
            # For MovePhysics, speed_m_s is crucial
            return MovePhysics(
                start_cell=start_cell,
                board=self.board,
                speed_m_s=speed_m_s,
                next_state_name=next_state_name, # Pass next_state_name here
            )
        elif physics_type == "IdlePhysics":
            # IdlePhysics might have a cooldown, but not a speed
            # Note: If IdlePhysics has a cooldown_duration_ms, it should be passed here.
            # Based on the provided snippet, it doesn't, so we'll omit it for now.
            return IdlePhysics(
                start_cell=start_cell,
                board=self.board,
                next_state_name=next_state_name, # Pass next_state_name here
            )
        # Add more physics types as needed (e.g., AttackPhysics, JumpPhysics)
        else:
            raise ValueError(f"Unknown physics type specified in config: {physics_type}")