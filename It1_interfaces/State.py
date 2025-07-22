class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        pass

    def set_transition(self, event: str, target: 'State'):
        pass

    def reset(self, cmd: Command):
        pass

    def update(self, now_ms: int) -> 'State':
        pass

    def process_command(self, cmd: Command, now_ms: int) -> 'State':
        pass

    def can_transition(self, now_ms: int) -> bool:
        pass

    def get_command(self) -> Optional[Command]:
        pass

    def get_graphics(self):
        pass

    def get_physics(self):
        pass

    def get_moves(self) -> Moves:
        pass
