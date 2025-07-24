import copy
from typing import Dict, Optional, Tuple
from .command import Command
from .moves import Moves
from .graphics import Graphics
from .physics import Physics, MovePhysics, IdlePhysics
import time
import logging # הוספת לוגינג לדיבוג טוב יותר

# הגדרת לוגר
logger = logging.getLogger(__name__)
# ניתן להגדיר רמת לוגינג (לדוגמה, DEBUG, INFO) וקונפיגורציה של פלט
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
# logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics,
                 state_name: str,
                 next_state_when_finished_name: Optional[str]):
        self._graphics = graphics
        self._physics = physics
        self._moves = moves
        self._transitions: Dict[str, 'State'] = {} # זה עדיין מילון, אבל נשתמש בו אחרת
        self._current_command: Optional[Command] = None
        self._state_name = state_name
        self._next_state_when_finished_name = next_state_when_finished_name
        self._started_at_ms: int = int(time.time() * 1000)

    def set_transition(self, event: str, target: 'State'):
        # חתימה ללא שינוי: set_transition(self, event, target)
        # פנימית: ה-target הוא אובייקט State המשמש כתבנית
        self._transitions[event] = target

    def reset(self, cmd: Optional[Command]):
        # חתימה ללא שינוי: reset(self, cmd)
        self._current_command = cmd
        self._graphics.reset(cmd=cmd)
        self._physics.reset(cmd=cmd)
        self._started_at_ms = int(time.time() * 1000)

    
    def update(self, dt: float) -> 'State':
        # logger.debug(f"State {self._state_name} update called.")
        
        self._graphics.update(dt)
        physics_cmd = self._physics.update(dt) 

        # 1. טיפול במעבר שנוצר ע"י סיום פעולת פיזיקה (כמו סיום תנועה)
        if physics_cmd is not None:
            # logger.info(f"[{physics_cmd.piece_id if physics_cmd else 'N/A'}] "
                        # f"[State.update] Physics returned command type: {physics_cmd.type}. "
                        # f"Attempting transition to: {physics_cmd.type}")
            
            target_state_template = self._transitions.get(physics_cmd.type) # <-- וודא שזה physics_cmd.type
            
            if target_state_template:
                new_state = copy.deepcopy(target_state_template) 
                
                final_pos_cell = self._physics.get_cell() 
                final_pos_m = self._physics.get_pos() 
                
                # יצירת מופע פיזיקה חדש עבור המצב הבא, עם המיקום המעודכן
                if isinstance(new_state._physics, IdlePhysics):
                    new_state_physics = IdlePhysics(
                        start_cell=final_pos_cell,
                        board=self._physics.board,
                        next_state_name=new_state._next_state_when_finished_name 
                    )
                elif isinstance(new_state._physics, Physics): 
                    new_state_physics = new_state._physics.__class__(
                        start_cell=final_pos_cell,
                        board=self._physics.board,
                        speed_m_s=getattr(new_state._physics, 'speed', 0.0), 
                        next_state_name=new_state._next_state_when_finished_name
                    )
                else:
                    # logger.warning(f"Unknown physics type for next state {new_state._state_name}. Cannot set initial position.")
                    new_state_physics = new_state._physics 
                    
                new_state_physics.cur_pos_m = final_pos_m 
                new_state._physics = new_state_physics 
                
                # **השינוי מתבצע כאן:**
                new_state.reset(physics_cmd) # <-- העבר את הפקודה שהפיזיקה יצרה
                # logger.info(f"[{physics_cmd.piece_id if physics_cmd else 'N/A'}] "
                            # f"Successfully transitioned from '{self._state_name}' to '{new_state._state_name}' via physics command.")
                return new_state
            # else:
            #     logger.warning(f"Warning: Target state '{physics_cmd.type}' not found in transitions for physics command from '{self._state_name}'. Staying in current state.")
        
        # 2. טיפול במעבר אוטומטי לאחר סיום גרפיקה ופיזיקה (למשל, מ-move ל-long_rest)
        # בלוק זה עשוי להיות כפילות אם הפיזיקה כבר מחזירה פקודה עם סוג המצב הבא.
        # ניתן לשקול לפשט את לוגיקת המעברים כך שרק בלוק אחד יטפל בהם.
        is_graphics_finished = self._graphics.is_finished()
        is_physics_finished = self._physics.is_finished(dt) # כאן dt הוא ה-now_ms

        if self._state_name != "idle" and self._next_state_when_finished_name and \
           is_graphics_finished and is_physics_finished:
            
            # logger.info(f"[{self._current_command.piece_id if self._current_command else 'N/A'}] "
            #             f"[State.update] State '{self._state_name}' finished automatically! "
            #             f"Attempting transition to: {self._next_state_when_finished_name}")
            
            # **השינוי מתבצע כאן:**
            # הפקודה החדשה צריכה להתאים למצב הבא (לדוגמה, "long_rest")
            # במקום להשתמש ב-self._current_command הישן.
            
            # וודא שאתה לוקח את ה-piece_id מהפקודה הנוכחית
            piece_id = self._current_command.piece_id if self._current_command else "N/A" # כדי למנוע שגיאה אם current_command הוא None

            # יצירת פקודה חדשה עם סוג המצב הבא
            new_command_for_next_state = Command(
                timestamp=dt, # עכשיו זה now_ms
                type=self._next_state_when_finished_name, # לדוגמה, "long_rest"
                piece_id=piece_id,
                params=[] 
            )

            next_state_template = self._transitions.get(self._next_state_when_finished_name)
            
            if next_state_template:
                new_state = copy.deepcopy(next_state_template)
                
                current_final_cell = self._physics.get_cell()
                current_final_pos_m = self._physics.get_pos()

                # יצירת מופע פיזיקה חדש למצב החדש, שתתחיל מהמיקום הנוכחי
                if isinstance(new_state._physics, IdlePhysics):
                    new_state_physics = IdlePhysics(
                        start_cell=current_final_cell,
                        board=self._physics.board,
                        next_state_name=new_state._next_state_when_finished_name
                    )
                elif isinstance(new_state._physics, Physics):
                    new_state_physics = new_state._physics.__class__(
                        start_cell=current_final_cell,
                        board=self._physics.board,
                        speed_m_s=getattr(new_state._physics, 'speed', 0.0),
                        next_state_name=new_state._next_state_when_finished_name
                    )
                else:
                    # logger.warning(f"Unknown physics type for next state {new_state._state_name}. Cannot set initial position.")
                    new_state_physics = new_state._physics
                    
                new_state_physics.cur_pos_m = current_final_pos_m 
                new_state._physics = new_state_physics 
                
                new_state.reset(new_command_for_next_state) # <-- העבר את הפקודה החדשה
                # logger.info(f"[{piece_id}] "
                            # f"Successfully transitioned from '{self._state_name}' to '{new_state._state_name}' automatically.")
                return new_state
            # else:
            #     logger.warning(f"Warning: Next state '{self._next_state_when_finished_name}' not found for automatic transition from '{self._state_name}'. Staying in current state.")

        return self


    def process_command(self, cmd: Command, now_ms: int) -> 'State':
        # חתימה ללא שינוי: process_command(self, cmd, now_ms) -> 'State'
        self._current_command = cmd
        # logger.info(f"[{cmd.piece_id}] Processing command: {cmd.type} from state {self._state_name}")

        # 1. טיפול מיוחד בפקודת "Move"
        if cmd.type == "Move":
            # לוודא שהכלי יכול לזוז רק ממצב idle. אם לא, פשוט נחזיר את המצב הנוכחי.
            # זהו המקום לאכוף את החוק "רק כאשר כלי במצב idle ניתן להזיז אותו או לקפוץ".
            if self._state_name != "idle":
                # logger.warning(f"[{cmd.piece_id}] Cannot move from state '{self._state_name}'. Must be in 'idle' to move.")
                return self # לא מאפשר תנועה אם לא במצב idle

            new_physics = self._physics.create_movement_to(
                target_cell=tuple(cmd.params),
                # יש לוודא שה-Physics.speed מוגדר ומגיע ממצב ה-Move ב-PieceFactory
                # אם speed=0, התנועה לא תתבצע
                speed=self._physics.speed # נניח שזו מהירות התנועה הכללית שרצו להשתמש בה
            )
            
            move_state_template = self._transitions.get("move")
            
            if move_state_template:
                new_state = copy.deepcopy(move_state_template)
                
                new_state._physics = new_physics
                
                # ודא שהגרפיקה של מצב ה-"move" היא לא בלולאה
                new_state._graphics.loop = False 
                new_state._graphics.reset(cmd=cmd) 
                
                new_state.reset(cmd) 
                # logger.info(f"[{cmd.piece_id}] Transitioning to 'move' state with target {cmd.params}.")
                return new_state
            else:
                # logger.error("Error: 'move' state template not found in transitions. Cannot initiate move.")
                return self 
        
        # 2. טיפול בפקודת "Jump" (בהתבסס על ההגדרה שלך)
        # זה דורש שיהיה מצב 'jump' מוגדר ב-transitions
        elif cmd.type == "Jump": 
            if self._state_name != "idle":
                # logger.warning(f"[{cmd.piece_id}] Cannot jump from state '{self._state_name}'. Must be in 'idle' to jump.")
                return self # לא מאפשר קפיצה אם לא במצב idle

            # נניח שגם ל-Jump יש פיזיקה משלה שנוצרת באופן דומה
            # אולי create_jump_to? או ש-create_movement_to מספיק אם הפיזיקה של קפיצה דומה
            # לצורך הדוגמה, נשתמש ב-create_movement_to עם פרמטרים מתאימים
            # ייתכן שתצטרכי להגדיר פונקציה כמו self._physics.create_jump_to()
            jump_physics = self._physics.create_movement_to( 
                target_cell=tuple(cmd.params), # נניח שהפקודה מכילה גם יעד לקפיצה
                speed=3.0 # מהירות קפיצה, כפי שהוגדר ב-jump.json
            )

            jump_state_template = self._transitions.get("jump")
            
            if jump_state_template:
                new_state = copy.deepcopy(jump_state_template)
                new_state._physics = jump_physics
                new_state._graphics.loop = False # קפיצה גם היא חד-פעמית
                new_state._graphics.reset(cmd=cmd)
                new_state.reset(cmd)
                # logger.info(f"[{cmd.piece_id}] Transitioning to 'jump' state with target {cmd.params}.")
                return new_state
            else:
                # logger.error("Error: 'jump' state template not found in transitions. Cannot initiate jump.")
                return self

        # 3. עבור פקודות אחרות (שאינן "Move" או "Jump")
        next_state_template = self._transitions.get(cmd.type)
        if next_state_template:
            # logger.info(f"[{cmd.piece_id}] Transitioning to: {cmd.type} state based on command.")
            new_state = copy.deepcopy(next_state_template)
            new_state.reset(cmd)
            return new_state

        # logger.warning(f"[{cmd.piece_id}] No transition defined for command type: {cmd.type} from state {self._state_name}. Staying in current state.")
        return self

    def can_transition(self, now_ms: int) -> bool:
        # חתימה ללא שינוי: can_transition(self, now_ms) -> bool
        return self._graphics.is_finished() and self._physics.is_finished(now_ms)

    # חתימות של פונקציות getter ללא שינוי
    def get_command(self) -> Optional[Command]:
        return self._current_command

    def get_graphics(self): return self._graphics
    def get_physics(self): return self._physics

    def get_moves(self) -> Moves:
        return self._moves