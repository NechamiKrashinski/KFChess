from typing import Tuple, Optional
from .command import Command
from .board import Board


class Physics:
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0):
        self.board = board
        self.speed = speed_m_s
        self.start_cell = start_cell # תא ההתחלה של הכלי
        self.cmd: Optional[Command] = None
        self.start_time_ms: Optional[int] = None
        self.cur_pos_m: Tuple[float, float] = (
            start_cell[0] * board.cell_W_m, # פינה שמאלית
            start_cell[1] * board.cell_H_m  # פינה עליונה
        )
        self.target_cell: Tuple[int, int] = start_cell


    def reset(self, cmd: Command):
        self.cmd = cmd
        self.start_time_ms = cmd.timestamp

    def update(self, now_ms: int) -> Command:
        return self.cmd

    def can_be_captured(self) -> bool:
        """ברירת מחדל: כלי במנוחה יכול להילכד."""
        return True

    def can_capture(self) -> bool:
        """ברירת מחדל: כלי במנוחה אינו יכול ללכוד."""
        return False

    def get_pos(self) -> Tuple[float, float]:
        return self.cur_pos_m

    def get_cell(self) -> Tuple[int, int]:
        """מחזירה את התא הנוכחי שבו הכלי נמצא."""
        # חישוב תא הלוח מתוך הקואורדינטות המטריות
        col = int(self.cur_pos_m[0] / self.board.cell_W_m)
        row = int(self.cur_pos_m[1] / self.board.cell_H_m)
        return (col, row)

    def create_movement_to(self, target_cell: Tuple[int, int], speed: float = 1.0) -> 'Physics':
        """
        מחזיר מופע חדש של MovePhysics שיזוז מהתא הנוכחי ל־target_cell.
        """
        move = MovePhysics(start_cell=self.get_cell(), board=self.board, speed_m_s=speed)
        move.end_cell = target_cell
        return move

class IdlePhysics(Physics):
    def update(self, now_ms: int) -> Command:
        return self.cmd


class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.end_cell: Tuple[int, int] = start_cell
        self.vector_m: Tuple[float, float] = (0.0, 0.0)
        self.duration_s: float = 0.0

    def reset(self, cmd: Command):
        super().reset(cmd)
        if cmd.type != "Move" or len(cmd.params) != 2:
            raise ValueError("Invalid command for MovePhysics")

        self.start_cell = self.get_cell() # קבע את תא ההתחלה האמיתי לפני תחילת התנועה
        self.end_cell = tuple(cmd.params)
        
        # חישוב וקטור התנועה ביחידות מטר
        dx = (self.end_cell[0] - self.start_cell[0]) * self.board.cell_W_m
        dy = (self.end_cell[1] - self.start_cell[1]) * self.board.cell_H_m
        self.vector_m = (dx, dy)
        
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.duration_s = distance / self.speed if self.speed > 0 else float("inf")

    def update(self, now_ms: int) -> Command:
        if self.start_time_ms is None:
            return self.cmd

        elapsed_s = (now_ms - self.start_time_ms) / 1000.0
        
        # 1. בדוק אם התנועה הסתיימה
        if elapsed_s >= self.duration_s:
            # הגדר את המיקום הסופי וסיים את התנועה
            self.cur_pos_m = (
                self.end_cell[0] * self.board.cell_W_m,
                self.end_cell[1] * self.board.cell_H_m
            )
            self.start_cell = self.end_cell
            # אולי תחזור למצב Idle כאן, או תמשיך לטפל בפקודה
            # כדי למנוע קריאה נוספת ל-MovePhysics עבור תנועה שהסתיימה
            # במקום להחזיר self.cmd, נרצה אולי להחזיר את הפקודה המקורית שקיבלה הפיזיקה
            # זה יכול להיות מורכב יותר, אז נתמקד בתיקון ה-ratio כרגע.
            
            # אם אין פה שימוש ב-ratio, אז אין צורך להגדיר אותו.
            # אבל אולי אתה רוצה לטפל במקרה של תנועה שהסתיימה על ידי מעבר למצב פיזיקה אחר (IdlePhysics)?
            # נניח בינתיים שזה בסדר להחזיר את ה-cmd הנוכחי.
            return self.cmd # התנועה הסתיימה, לא צריך לחשב ratio

        # 2. אם התנועה עדיין בעיצומה, חשב את ratio
        # המקרה שבו התנועה עדיין מתבצעת
        if self.duration_s > 0: # וודא שאין חלוקה באפס
            ratio = elapsed_s / self.duration_s
        else: # אם duration_s הוא 0 (תנועה מיידית או משהו כזה)
            ratio = 1.0 # או כל ערך אחר הגיוני למצב מיידי

        # חשב את המיקום המבוסס על אינטרפולציה
        self.cur_pos_m = (
            self.start_cell[0] * self.board.cell_W_m + self.vector_m[0] * ratio,
            self.start_cell[1] * self.board.cell_H_m + self.vector_m[1] * ratio
        )
        return self.cmd

    def can_be_captured(self) -> bool:
        """כלי בתנועה לא אמור להילכד באמצע המהלך."""
        return False

    def can_capture(self) -> bool:
        """כלי בתנועה *כן* יכול ללכוד בסיום התנועה שלו."""
        return True
    
    

