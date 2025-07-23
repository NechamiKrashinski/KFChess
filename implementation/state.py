import cmd
from typing import Dict, Optional
from .command import Command
from .moves import Moves
from .graphics import Graphics
from .physics import Physics


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        self._graphics = graphics
        self._physics = physics
        self._moves = moves
        self._transitions: Dict[str, 'State'] = {}
        self._current_command: Optional[Command] = None

    def set_transition(self, event: str, target: 'State'):
        self._transitions[event] = target

    def reset(self, cmd: Command):
        self._current_command = cmd
        self._graphics.reset(cmd=cmd)
        self._physics.reset(cmd=cmd)

    def update(self, now_ms: int) -> 'State':
        self._graphics.update(now_ms)
        cmd = self._physics.update(now_ms)

        if cmd is not None:
            return self.process_command(cmd, now_ms)

        return self

    def process_command(self, cmd: Command, now_ms: int) -> 'State':
       
        self._current_command = cmd
        # print(f"[{cmd.piece_id}] Command type: {cmd.type}")
        print(f"[{cmd.piece_id}] transition: {self._current_command.type} → {cmd.type}")

        if cmd.type == "Move":
            new_physics = self._physics.create_movement_to(tuple(cmd.params))
            new_state = State(
                moves=self._moves,
                graphics=self._graphics.copy(),
                physics=new_physics
            )
            new_state.reset(cmd)
            return new_state

        next_state = self._transitions.get(cmd.type)
        if next_state:
            next_state.reset(cmd)
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
