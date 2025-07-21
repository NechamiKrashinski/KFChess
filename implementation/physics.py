from typing import Tuple, Optional
from .command import Command
from .board import Board


class Physics:
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0):
        self.board = board
        self.speed = speed_m_s
        self.start_cell = start_cell
        self.cmd: Optional[Command] = None
        self.start_time_ms: Optional[int] = None
        self.cur_pos_m: Tuple[float, float] = (
            start_cell[0] * board.cell_W_m,
            start_cell[1] * board.cell_H_m
        )

    def reset(self, cmd: Command):
        self.cmd = cmd
        self.start_time_ms = cmd.timestamp

    def update(self, now_ms: int) -> Command:
        return self.cmd

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return True

    def get_pos(self) -> Tuple[float, float]:
        return self.cur_pos_m


class IdlePhysics(Physics):
    def update(self, now_ms: int) -> Command:
        return self.cmd


class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.end_cell: Tuple[int, int] = start_cell  # אתחול
        self.vector_m: Tuple[float, float] = (0.0, 0.0) # אתחול
        self.duration_s: float = 0.0  # אתחול

    def reset(self, cmd: Command):
        super().reset(cmd)
        if cmd.type != "Move" or len(cmd.params) != 2:
            raise ValueError("Invalid command for MovePhysics")

        self.end_cell = tuple(cmd.params)
        dx = (self.end_cell[0] - self.start_cell[0]) * self.board.cell_W_m
        dy = (self.end_cell[1] - self.start_cell[1]) * self.board.cell_H_m
        self.vector_m = (dx, dy)
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.duration_s = distance / self.speed if self.speed > 0 else float("inf")

    def update(self, now_ms: int) -> Command:
        if self.start_time_ms is None:
            return self.cmd

        elapsed_s = (now_ms - self.start_time_ms) / 1000.0
        if elapsed_s >= self.duration_s:
            # Movement finished
            self.cur_pos_m = (
                self.end_cell[0] * self.board.cell_W_m,
                self.end_cell[1] * self.board.cell_H_m
            )
        else:
            # Interpolated position
            ratio = elapsed_s / self.duration_s
            self.cur_pos_m = (
                self.start_cell[0] * self.board.cell_W_m + self.vector_m[0] * ratio,
                self.start_cell[1] * self.board.cell_H_m + self.vector_m[1] * ratio
            )
        return self.cmd

    def can_be_captured(self) -> bool:
        return False

    def can_capture(self) -> bool:
        return False
