import cmd
from typing import Dict, Optional
from .command import Command
from .moves import Moves
from .graphics import Graphics
from .physics import Physics


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """
        אתחול מחלקת מצב עם המודולים החשובים:
        - moves: ניהול תנועות הלוח
        - graphics: ניהול גרפיקה ועדכונים ויזואליים
        - physics: ניהול פיזיקה, תזמון, ופקודות משתמש
        """
        self._graphics = graphics
        self._physics = physics
        self._moves = moves
        self._transitions: Dict[str, 'State'] = {}  # מיפוי אירוע -> מצב הבא
        self._current_command: Optional[Command] = None  # הפקודה שהובילה למצב הנוכחי

    def set_transition(self, event: str, target: 'State'):
        """
        הגדרת מעבר בין מצבים: בעת אירוע מסוים נעבור למצב אחר.
        :param event: סוג הפקודה או האירוע (string)
        :param target: אובייקט State שאליו נעבור
        """
        self._transitions[event] = target

    def reset(self, cmd: Command):
        """
        אתחול המצב עם פקודה חדשה (לדוגמה תחילת תור).
        מאפס את המודולים הגרפיים והפיזיקליים.
        שומר את הפקודה כפקודה נוכחית.
        """
        self._current_command = cmd
        self._graphics.reset(cmd=cmd)
        self._physics.reset(cmd=cmd)

    def update(self, now_ms: int) -> 'State':
        """
        עדכון מצב בזמן אמת (time step).
        מבצע עדכון גרפי ופיזיקלי.
        אם מתקבלת פקודה חדשה מהפיזיקה - מעבד אותה ועובר למצב הבא.
        אם לא, נשאר במצב הנוכחי.
        """
        self._graphics.update(now_ms)
        cmd = self._physics.update(now_ms)

        if cmd is not None:
            return self.process_command(cmd, now_ms)

        return self

    # def process_command(self, cmd: Command, now_ms: int) -> 'State':
    #     """
    #     עיבוד פקודה - אם קיימת הגדרת מעבר למצב אחר לפי סוג הפקודה,
    #     מבצע מעבר, אחרת נשאר באותו מצב.
    #     """
    #     self._current_command = cmd
    #     next_state = self._transitions.get(cmd.type)

    #     if next_state is None:
    #         return self  # אין מעבר תקף, נשאר באותו מצב

    #     next_state.reset(cmd)
    #     return next_state
    def process_command(self, cmd: Command, now_ms: int) -> 'State':
        self._current_command = cmd

        if cmd.type == "Move":
            new_physics = self._physics.create_movement_to(tuple(cmd.params))
            new_state = State(
                moves=self._moves,
                graphics=self._graphics,
                physics=new_physics
            )
            new_state.reset(cmd)
            return new_state

        next_state = self._transitions.get(cmd.type)
        if next_state is None:
            return self
        next_state.reset(cmd)
        return next_state



    def can_transition(self, now_ms: int) -> bool:
        """
        פונקציה שניתן להרחיב לפי הצורך לבדוק האם ניתן לעבור למצב הבא,
        למשל על פי תזמון או תנאי מערכת.
        כברירת מחדל מחזירה True.
        """
        return True

    def get_command(self) -> Optional[Command]:
        """
        מחזירה את הפקודה שהובילה למצב הנוכחי,
        או None אם לא קיימת כזו.
        """
        return self._current_command

    def get_graphics(self): return self._graphics
    def get_physics(self): return self._physics


    def get_moves(self) -> Moves:
        return self._moves
