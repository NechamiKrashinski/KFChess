# Physics.py
from typing import Tuple, Optional
from .command import Command
from .board import Board
import time

class Physics:
    # **שינוי חדש: מילון זמני קירור קבועים לפי שם המצב**
    # (הועבר למקום אחר או יטופל ב-State, Physics לא צריך לדעת על cooldowns)
    # _STATE_COOLDOWNS_MS = { ... }

    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0,
                 next_state_name: str = "idle"): # הסרנו current_state_name מפה
        self.board = board
        self.speed = speed_m_s
        self.start_cell = start_cell
        self.cmd: Optional[Command] = None
        self.start_time_ms: Optional[int] = None # זמן התחלת הפקודה שהתקבלה
        
        self.cur_pos_m: Tuple[float, float] = (
            start_cell[0] * board.cell_W_m,
            start_cell[1] * board.cell_H_m
        )
        self.target_cell: Tuple[int, int] = start_cell
        self._next_state_name = next_state_name
        
        # Physics לא צריך לנהל cooldowns. ה-State אחראי לזה.
        # self._state_started_time_ms: Optional[int] = None
        
    def get_pos(self) -> Tuple[float, float]:
        return self.cur_pos_m
    
    def get_cell(self) -> Tuple[int, int]:
        """Returns the current cell where the piece is located."""
        # חשוב: round לפני int כדי למנוע טעויות עיגול (floor)
        col = int(round(self.cur_pos_m[0] / self.board.cell_W_m))
        row = int(round(self.cur_pos_m[1] / self.board.cell_H_m))
        return (col, row)
    
    def reset(self, cmd: Command): # cmd חייב להיות קיים ב-reset
        self.cmd = cmd
        self.start_time_ms = cmd.timestamp # זמן התחלת המצב הוא זמן הפקודה
        # אין צורך ב-self._state_started_time_ms כאן, זה שייך ל-State
        
    def update(self, now_ms: float) -> Optional[Command]:
        # print("[DEBUG] Physics update called, but no specific logic implemented.")
        # מתודת update ב-Physics הבסיסי לא עושה כלום, רק ב-MovePhysics
        return None

    def is_finished(self, now_ms: int) -> bool:
        # מצב פיזיקה בסיסי תמיד 'מסיים' אם אין לו לוגיקת תנועה
        return True

    def create_movement_to(self, target_cell: Tuple[int, int], speed: float = 1.0) -> 'MovePhysics':
        # הפונקציה הזו יוצרת אובייקט MovePhysics, היא לא מעדכנת את הפיזיקה הנוכחית.
        move = MovePhysics(
            start_cell=self.get_cell(), # תא ההתחלה של התנועה הוא התא הנוכחי של הכלי
            board=self.board,
            speed_m_s=speed,
            next_state_name=self._next_state_name, 
            start_pos_m=self.cur_pos_m # הוסף את המיקום הנוכחי כאן
        )
        move.end_cell = target_cell # קובע את תא היעד
        return move


class IdlePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 0.0,
                 next_state_name: str = "idle"): # הסרנו current_state_name
        super().__init__(start_cell, board, speed_m_s, next_state_name)
        self._idle_timer = 0.0
        self._idle_duration = 0.0

    def update(self, now_ms: float) -> Optional[Command]:
        # print("[DEBUG] IdlePhysics update called, but does not change position.")
        return None # IdlePhysics לא משנה מיקום ולא יוצר פקודה בעצמו

    def is_finished(self, now_ms: int) -> bool:
        return True # מצב Idle תמיד "גמור" מבחינת תנועה


class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int], board: Board,
                 speed_m_s: float = 1.0, next_state_name: str = "idle",
                 start_pos_m: Optional[Tuple[float, float]] = None): # **הוסף פרמטר**
        super().__init__(start_cell, board, speed_m_s, next_state_name)

        if start_pos_m:
            self.cur_pos_m = start_pos_m
        self.end_cell: Tuple[int, int] = start_cell # יוגדר ב-reset
        self.vector_m: Tuple[float, float] = (0.0, 0.0)
        self.duration_s: float = 0.0
        self._is_movement_finished = False

    def reset(self, cmd: Command):
        super().reset(cmd) # זה מאתחל את start_time_ms
        self._is_movement_finished = False
        
        if cmd.type != "Move" or len(cmd.params) != 2:
            raise ValueError("Invalid command for MovePhysics: Type must be 'Move' and params must have 2 elements.")
        try:
            target_col = int(cmd.params[0])
            target_row = int(cmd.params[1])
            self.end_cell = (target_col, target_row)
        except (ValueError, TypeError):
            raise ValueError("Invalid command for MovePhysics: Params must be convertible to integers.")
        
        # חשוב: start_cell צריך להיות המיקום הנוכחי של הכלי בעת התחלת התנועה
        # במקרה שלנו, get_cell() אמור להחזיר את המיקום הנוכחי של cur_pos_m
        # (אבל ה-start_cell של הפזיקה הושם כבר באיתחול)
        # נוודא שה-cur_pos_m ההתחלתי יהיה מתאם ל-start_cell
        self.start_cell = self.get_cell() # **וודא שתא ההתחלה הוא התא הנוכחי**
        self.cur_pos_m = (
            self.start_cell[0] * self.board.cell_W_m,
            self.start_cell[1] * self.board.cell_H_m
        )
        dx = (self.end_cell[0] - self.start_cell[0]) * self.board.cell_W_m
        dy = (self.end_cell[1] - self.start_cell[1]) * self.board.cell_H_m
        self.vector_m = (dx, dy)
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        self.duration_s = distance / self.speed if self.speed > 0 else 0.0 
        
        # הוסף הדפסות לניפוי באגים כאן ב-reset()
        print(f"DEBUG MovePhysics.reset(): Piece {self.cmd.piece_id}. From ({self.start_cell}) to ({self.end_cell}). Distance: {distance:.2f} m. Duration: {self.duration_s:.2f} s. Start Time: {self.start_time_ms} ms.")


    def update(self, dt: float) -> Optional[Command]:
        # print("[DEBUG] MovePhysics update called.")
        if self._is_movement_finished:
            return None

        if self.start_time_ms is None: # התנועה עדיין לא אותחלה
            return None
            
        if self.duration_s == 0: # תנועה מיידית (לדוגמה, לאותו תא או מהירות 0)
            self.cur_pos_m = (
                self.end_cell[0] * self.board.cell_W_m,
                self.end_cell[1] * self.board.cell_H_m
            )
            self.start_cell = self.end_cell # עדכן את תא ההתחלה להיות תא היעד
            self._is_movement_finished = True
            print(f"DEBUG MovePhysics.update(): Piece {self.cmd.piece_id} instant move to {self.get_cell()}.")
            
            # כשה-MovePhysics מסיים, הוא מחזיר פקודה עם סוג המצב הבא
            return Command(
                timestamp=dt,
                type=self._next_state_name,
                piece_id=self.cmd.piece_id,
                params=[] 
            )

        elapsed_ms = dt - self.start_time_ms
        elapsed_s = elapsed_ms / 1000.0

        if elapsed_s >= self.duration_s:
            # הגיע ליעד
            self.cur_pos_m = (
                self.end_cell[0] * self.board.cell_W_m,
                self.end_cell[1] * self.board.cell_H_m
            )
            self.start_cell = self.end_cell # עדכן את תא ההתחלה להיות תא היעד
            self._is_movement_finished = True
            print(f"DEBUG MovePhysics.update(): Piece {self.cmd.piece_id} arrived at {self.get_cell()}.")
            
            # כשה-MovePhysics מסיים, הוא מחזיר פקודה עם סוג המצב הבא
            return Command(
                timestamp=dt,
                type=self._next_state_name,
                piece_id=self.cmd.piece_id,
                params=[] 
            )

        # חישוב המיקום הנוכחי במהלך התנועה
        ratio = elapsed_s / self.duration_s
        
        current_x_m = self.start_cell[0] * self.board.cell_W_m + self.vector_m[0] * ratio
        current_y_m = self.start_cell[1] * self.board.cell_H_m + self.vector_m[1] * ratio
        self.cur_pos_m = (current_x_m, current_y_m)
        
        # הדפסת מיקום נוכחי לוודא שהוא משתנה - ורבוזי מאוד, רק כשמנפים
        # print(f"DEBUG MovePhysics.update(): Piece {self.cmd.piece_id} moving. Current Pos (m): {self.cur_pos_m}. Cell: {self.get_cell()}")

        return None

    def is_finished(self, now_ms: int) -> bool:
        # כאן ה-is_finished עבור MovePhysics צריך לשקף את סיום התנועה
        return self._is_movement_finished