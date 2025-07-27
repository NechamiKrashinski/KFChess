import cmd
from typing import Dict, Optional
from .command import Command
from .moves import Moves
from .graphics import Graphics
from .physics import Physics


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics, state: str):
        self._graphics = graphics
        self._physics = physics
        self._moves = moves
        self._transitions: Dict[str, 'State'] = {}
        self._current_command: Optional[Command] = None
        self._current_state = state
 
    def set_transition(self, event: str, target: 'State'):
        self._transitions[event] = target

    def reset(self, cmd: Command):
        self._current_command = cmd
        self._graphics.reset(cmd=cmd)
        self._physics.reset(cmd=cmd)

    def update(self, now_ms: int) -> 'State':
        piece_id_for_debug = self._current_command.piece_id if self._current_command else "UNKNOWN_PIECE"
        
        self._graphics.update(now_ms)
        physics_cmd = self._physics.update(now_ms)

        if physics_cmd is not None:
            return self.process_command(physics_cmd, now_ms)

        if not self._graphics.loop and self._graphics.is_finished():
            piece_id = self._current_command.piece_id if self._current_command else "unknown"
            finished_rest_cmd = Command(
                timestamp=now_ms,
                type="finished_rest",
                piece_id=piece_id,
                params=[]
            )
            return self.process_command(finished_rest_cmd, now_ms)
        
        return self

    def process_command(self, cmd: Command, now_ms: int) -> 'State':
        self._current_command = cmd
        
        next_state = self._transitions.get(cmd.type)
        
        if next_state:
            current_pos = self._physics.get_pos()
            current_cell = self._physics.get_cell()
            next_state.reset(cmd)
            next_state.get_physics().cur_pos_m = current_pos
            next_state.get_physics().start_cell = current_cell
            return next_state
        
        return self


    def can_transition(self, now_ms: int) -> bool:
        return True

    def get_command(self) -> Optional[Command]:
        return self._current_command

    def get_graphics(self): return self._graphics
    def get_physics(self): return self._physics

    def get_moves(self) -> Moves:
        return self._moves
    
    def get_state(self) -> str:
        return self._current_state