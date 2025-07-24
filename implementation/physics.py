from typing import Tuple, Optional
from .command import Command
from .board import Board


class Physics:
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0, next_state_name="idle"):
        self.board = board
        self.speed = speed_m_s
        self.start_cell = start_cell
        self.cmd: Optional[Command] = None
        self.start_time_ms: Optional[int] = None
        self.cur_pos_m: Tuple[float, float] = (
            start_cell[0] * board.cell_W_m,
            start_cell[1] * board.cell_H_m
        )
        self.target_cell: Tuple[int, int] = start_cell
        self._next_state_name = next_state_name

    def reset(self, cmd: Command):
        self.cmd = cmd
        self.start_time_ms = cmd.timestamp

    def update(self, now_ms: int) -> Command:
        return self.cmd

    def can_be_captured(self) -> bool:
        """Default: A piece at rest can be captured."""
        return True

    def can_capture(self) -> bool:
        """Default: A piece at rest cannot capture."""
        return False

    def get_pos(self) -> Tuple[float, float]:
        return self.cur_pos_m

    def get_cell(self) -> Tuple[int, int]:
        """Returns the current cell where the piece is located."""
        col = int(self.cur_pos_m[0] / self.board.cell_W_m)
        row = int(self.cur_pos_m[1] / self.board.cell_H_m)
        return (col, row)

    def create_movement_to(self, target_cell: Tuple[int, int], speed: float = 1.0) -> 'Physics':
        """Returns a new instance of MovePhysics that will move from the current cell to target_cell."""
        move = MovePhysics(
        start_cell=self.get_cell(),
        board=self.board,
        speed_m_s=speed,
        next_state_name=self._next_state_name 
        )
        move.end_cell = target_cell
        return move


class IdlePhysics(Physics):
    def update(self, now_ms: int) -> Command:
        return self.cmd


class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board,
                 speed_m_s: float = 1.0,
                 next_state_name: str = "idle"):
        super().__init__(start_cell, board, speed_m_s, next_state_name)
        self.end_cell: Tuple[int, int] = start_cell
        self.vector_m: Tuple[float, float] = (0.0, 0.0)
        self.duration_s: float = 0.0

    def reset(self, cmd: Command):
        super().reset(cmd)
        
        # שלב 1: בדיקת סוג הפקודה ומספר הפרמטרים
        if cmd.type != "Move" or len(cmd.params) != 2:
            raise ValueError("Invalid command for MovePhysics: Type must be 'Move' and params must have 2 elements.")

        # שלב 2: בדיקת סוג הפרמטרים
        # ודא ששני הפרמטרים ניתנים להמרה ל-int
        try:
            target_col = int(cmd.params[0])
            target_row = int(cmd.params[1])
            self.end_cell = (target_col, target_row)
        except (ValueError, TypeError): # תופס גם אם זה לא ניתן להמרה (כמו 'a')
            raise ValueError("Invalid command for MovePhysics: Params must be convertible to integers.")

        # כעת כש-end_cell מוגדר ובעל סוגים נכונים, ניתן לבצע חישובים
        if cmd.source_cell: # אם תא המקור קיים בפקודה
            self.start_cell = cmd.source_cell
            self.cur_pos_m = (
                self.start_cell[0] * self.board.cell_W_m,
                self.start_cell[1] * self.board.cell_H_m
            )
        else:
            # זהו קוד גיבוי/אזהרה למקרה ש-source_cell איכשהו חסר (לא אמור לקרות)
            print(f"Warning: Command for {cmd.piece_id} (Move) is missing source_cell. Fallback to current physics cell.")
            self.start_cell = self.get_cell() # חזרה להתנהגות הקודמת במקרה חירום
        dx = (self.end_cell[0] - self.start_cell[0]) * self.board.cell_W_m
        dy = (self.end_cell[1] - self.start_cell[1]) * self.board.cell_H_m
        self.vector_m = (dx, dy)
        
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.duration_s = distance / self.speed if self.speed > 0 else float("inf")

    def update(self, now_ms: int) -> Optional[Command]:
        if self.start_time_ms is None:
            return None

        elapsed_s = (now_ms - self.start_time_ms) / 1000.0

        if elapsed_s >= self.duration_s:
            self.cur_pos_m = (
                self.end_cell[0] * self.board.cell_W_m,
                self.end_cell[1] * self.board.cell_H_m
            )
            self.start_cell = self.end_cell

            return Command(
                timestamp=now_ms,
                type="finished_movement",
                piece_id=self.cmd.piece_id,
                params=self.cmd.params
            )

        ratio = elapsed_s / self.duration_s if self.duration_s > 0 else 1.0
        self.cur_pos_m = (
            self.start_cell[0] * self.board.cell_W_m + self.vector_m[0] * ratio,
            self.start_cell[1] * self.board.cell_H_m + self.vector_m[1] * ratio
        )
        return None

    def can_be_captured(self) -> bool:
        """A piece in motion should not be captured mid-move."""
        return False

    def can_capture(self) -> bool:
        """A piece in motion can capture at the end of its movement."""
        return True
