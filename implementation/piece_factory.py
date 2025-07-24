import pathlib
from typing import Dict, Tuple, List, Optional
import json
import copy
import logging

from .board import Board
from .graphics_factory import GraphicsFactory
from .moves import Moves
from .physics_factory import PhysicsFactory # ייבוא PhysicsFactory
from .piece import Piece
from .state import State
from .physics import IdlePhysics, MovePhysics, Physics # וודא שאתה מייבא את כל מחלקות הפיזיקה

logger = logging.getLogger(__name__)

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.moves_lib: Dict[str, Moves] = {}
        self.state_templates: Dict[str, Dict[str, State]] = {} 
        self.graphics_factory = GraphicsFactory(board=self.board)
        # PhysicsFactory לא יכולה ליצור את הטיפוס הנכון מ-cfg בלבד.
        # אנו נצטרך לייצר את אובייקטי הפיזיקה ישירות כאן או ב-State.
        self.physics_factory = PhysicsFactory(board=self.board) # עדיין נשמור עליו אם יש לו שימושים אחרים
        self._load_piece_templates()

    def _load_piece_templates(self):
        logger.info("Loading piece templates...")
        for piece_dir in self.pieces_root.iterdir():
            if not piece_dir.is_dir():
                continue

            piece_type = piece_dir.name
            main_cfg_path = piece_dir / "config.json"
            
            if not main_cfg_path.exists():
                logger.warning(f"No config.json found for piece '{piece_type}'. Skipping.")
                continue

            with open(main_cfg_path, 'r') as f:
                main_cfg = json.load(f)

            moves_file = main_cfg.get("moves")
            if moves_file:
                moves_path = piece_dir / moves_file
                if moves_path.exists():
                    self.moves_lib[piece_type] = Moves(
                        moves_txt_path=moves_path,
                        dims=(self.board.H_cells, self.board.W_cells)
                    )
                else:
                    logger.warning(f"Moves file not found for piece '{piece_type}' at {moves_path}")
            
            initial_state_name = main_cfg.get("initial_state")
            state_names = main_cfg.get("states", [])
            
            if initial_state_name and state_names:
                all_piece_states = self._build_state_machine(
                    piece_dir=piece_dir,
                    piece_type=piece_type,
                    state_names=state_names,
                    main_cfg=main_cfg 
                )
                if all_piece_states:
                    self.state_templates[piece_type] = all_piece_states
                    logger.info(f"Loaded templates for piece type '{piece_type}': {list(all_piece_states.keys())}")


    def _build_state_machine(self,
                             piece_dir: pathlib.Path,
                             piece_type: str,
                             state_names: List[str],
                             main_cfg: Dict) -> Dict[str, State]:
        """
        Builds a dictionary of state templates for a piece from its directory.
        These are the master templates that will be deep-copied for each new piece.
        """
        states_dir = piece_dir / "states"
        state_objects: Dict[str, State] = {}
        
        # Stage 1: Create all State objects (templates) without linking them yet
        for state_name in state_names:
            state_cfg_path = states_dir / state_name / "config.json"
            if not state_cfg_path.exists():
                raise FileNotFoundError(f"Config file not found for state '{state_name}': {state_cfg_path}")
            
            with open(state_cfg_path, 'r') as f:
                cfg = json.load(f)

            graphics = self.graphics_factory.load(
                sprites_dir=states_dir / state_name / "sprites",
                cfg=cfg
            )
            
            # **שינוי מהותי כאן:** יצירת אובייקטי הפיזיקה בהתבסס על שם המצב (ולא רק על cfg)
            physics_speed = cfg.get("physics", {}).get("speed_m_per_sec", 0.0)
            next_state_when_finished_name = cfg.get("physics", {}).get("next_state_when_finished")

            physics: Physics # הגדרת טיפוס
            if state_name == "move" or state_name == "jump":
                # מצבים אלה דורשים פיזיקת תנועה (MovePhysics)
                physics = MovePhysics(
                    start_cell=(0, 0), # placeholder
                    board=self.board,
                    speed_m_s=physics_speed,
                    next_state_name=next_state_when_finished_name # This is used by Physics to return correct command type
                )
            elif state_name in ["idle", "long_rest", "short_rest"]:
                # מצבים אלה דורשים פיזיקה סטטית (IdlePhysics)
                physics = IdlePhysics(
                    start_cell=(0, 0), # placeholder
                    board=self.board,
                    # IdlePhysics לא צריכה speed_m_s, אבל אם יש, אפשר להעביר
                    next_state_name=next_state_when_finished_name
                )
            else:
                # ברירת מחדל או טיפול במצבים לא ידועים
                logger.warning(f"Unknown state type '{state_name}' for physics. Defaulting to IdlePhysics.")
                physics = IdlePhysics(
                    start_cell=(0, 0), # placeholder
                    board=self.board,
                    next_state_name=next_state_when_finished_name
                )
            
            state_objects[state_name] = State(
                moves=self.moves_lib[piece_type], # ה-Moves אובייקט ייקשר רק פעם אחת לטמפלט
                graphics=graphics,
                physics=physics,
                state_name=state_name,
                next_state_when_finished_name=next_state_when_finished_name
            )
            logger.debug(f"Created state template '{state_name}' for piece '{piece_type}'.")

        # Stage 2: Link the state templates
        for state_name, state_obj in state_objects.items():
            # 1. Automatic transitions based on physics finish (like move -> long_rest)
            if state_obj._next_state_when_finished_name and \
               state_obj._next_state_when_finished_name in state_objects:
                    transition_event_name = state_obj._next_state_when_finished_name 
                
                    state_obj.set_transition(
                    event=transition_event_name, # <-- השינוי המרכזי כאן
                    target=state_objects[state_obj._next_state_when_finished_name]
                )
                    logger.debug(f"Template for '{state_name}' linked automatic transition to '{state_obj._next_state_when_finished_name}'.")

            # 2. Command-based transitions (like Idle -> Move, Idle -> Jump)
            if state_name == "idle":
                if "move" in state_objects:
                    state_obj.set_transition(event="move", target=state_objects["move"])
                    logger.debug(f"Template for 'idle' hardcoded link 'Move' to 'move'.")
                if "jump" in state_objects:
                    state_obj.set_transition(event="jump", target=state_objects["jump"])
                    logger.debug(f"Template for 'idle' hardcoded link 'Jump' to 'jump'.")
            
            # Other potential command-based transitions (e.g., if "long_rest" could be interrupted by a "WakeUp" command)
            # This is less common for rest states, as they mostly transition automatically.
            # However, if there was a command "WakeUp" that explicitly moves from LongRest to Idle:
            # if state_name == "long_rest" and "idle" in state_objects:
            #     state_obj.set_transition(event="WakeUp", target=state_objects["idle"])
            # if state_name == "short_rest" and "idle" in state_objects:
            #     state_obj.set_transition(event="WakeUp", target=state_objects["idle"])


        return state_objects

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """
        Creates a new Piece instance with its own independent state machine.
        """
        if p_type not in self.state_templates:
            raise ValueError(f"Piece type '{p_type}' not found in loaded templates.")

        main_cfg_path = self.pieces_root / p_type / "config.json"
        with open(main_cfg_path, 'r') as f:
            main_cfg = json.load(f)
        initial_state_name = main_cfg.get("initial_state")
        
        if not initial_state_name:
            raise ValueError(f"Initial state not defined for piece type '{p_type}' in config.json.")

        logger.info(f"Creating new piece of type '{p_type}' at cell {cell}.")
        
        copied_states: Dict[str, State] = {}
        for state_name, state_template in self.state_templates[p_type].items():
            # **שינוי חשוב:** עכשיו אנחנו בטוחים שהטמפלט עצמו הוא מהטיפוס הנכון
            # לכן, deepcopy של הטמפלט אמור לשמור על טיפוס הפיזיקה.
            new_state = copy.deepcopy(state_template) 
            
            # **עדכון פרמטרים בפיזיקה המשוכפלת:**
            # חשוב לעדכן את המיקום ההתחלתי ואת הלוח עבור כל אובייקט פיזיקה ב-copied_states
            # (כי הם עדיין ב-(0,0) מהטמפלט)
            new_physics = new_state.get_physics()
            new_physics.board = self.board # וודא שהלוח מעודכן
            new_physics.cur_pos_m = (
                cell[0] * self.board.cell_W_m,
                cell[1] * self.board.cell_H_m
            )
            new_physics.start_cell = cell 
            
            # אם יש לוגיקת אתחול ספציפית ל-MovePhysics, היא צריכה להיות כאן או ב-State.reset
            # כרגע, State.process_command הוא זה שמטפל ביעד התנועה.
            
            copied_states[state_name] = new_state
            logger.debug(f"Piece '{p_type}' copied state '{state_name}' initialized physics for cell {cell}.")

        # Re-link the transitions within the copied states to point to other copied states
        for state_name, state_obj in copied_states.items():
            original_template = self.state_templates[p_type][state_name]
            state_obj._transitions = {}
            # ה-deepcopy כבר יצר מילון _transitions חדש עבור state_obj.
            # אנחנו רק צריכים לעדכן את ההפניות בתוכו שיובילו לאובייקטי copied_states.
            # נרוקן ונמלא מחדש כדי לוודא שאין הפניות ישנות לטמפלטים המקוריים
            # state_obj._transitions = {} 

            for event, target_template_state in original_template._transitions.items():
                if target_template_state._state_name in copied_states:
                    state_obj.set_transition(event, copied_states[target_template_state._state_name])
                    logger.debug(f"Piece '{p_type}' copied state '{state_name}' relinked '{event}' to '{target_template_state._state_name}'.")
                else:
                    logger.warning(f"Deep copy transition target '{target_template_state._state_name}' not found for event '{event}' in copied state '{state_name}' of piece '{p_type}'. This transition might be broken.")
            
        # Get the initial state for the new piece from the copied set
        initial_state = copied_states.get(initial_state_name)
        if not initial_state:
            raise ValueError(f"Initial state '{initial_state_name}' not found for piece type '{p_type}' in copied states. This indicates a configuration error or deep copy issue.")

        # מכיוון שעדכנו את הפיזיקה לכל ה-copied_states בלולאה למעלה, אין צורך לעדכן כאן שוב.
        # רק נוודא שה-initial_state אכן מצביע על הפיזיקה הנכונה במיקום הנכון.
        logger.info(f"Initial state '{initial_state_name}' physics for piece '{p_type}' confirmed at starting cell {cell}.")

        # Assign the correct moves object to the initial state (and by extension, to all copied states)
        # Assuming Moves is stateless per piece_type, linking the same Moves object from moves_lib is fine.
        for state_obj in copied_states.values():
            state_obj._moves = self.moves_lib[p_type]

        return Piece(
            piece_id=f"{p_type}_{cell[0]}_{cell[1]}",
            init_state=initial_state
        )