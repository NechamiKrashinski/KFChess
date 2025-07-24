import pathlib
from typing import Dict, Tuple, List, Optional
import json
import copy
import logging

from .board import Board
from .graphics_factory import GraphicsFactory
from .moves import Moves
from .physics_factory import PhysicsFactory
from .piece import Piece
from .state import State
from .physics import IdlePhysics, MovePhysics, Physics

logger = logging.getLogger(__name__)

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.moves_lib: Dict[str, Moves] = {}
        self.state_templates: Dict[str, Dict[str, State]] = {}
        self.graphics_factory = GraphicsFactory(board=self.board)
        self.physics_factory = PhysicsFactory(board=self.board)
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
        states_dir = piece_dir / "states"
        state_objects: Dict[str, State] = {}
        
        for state_name in state_names:
            state_cfg_path = states_dir / state_name / "config.json"
            if not state_cfg_path.exists():
                raise FileNotFoundError(f"Config file not found for state '{state_name}': {state_cfg_path}")
            
            with open(state_cfg_path, 'r') as f:
                cfg = json.load(f)
            
             # --- START FIX: Inject 'type' into cfg based on state_name ---
            physics_type_determined_by_state_name = "IdlePhysics" # ברירת מחדל
            
            if state_name == "move":
                physics_type_determined_by_state_name = "MovePhysics"
            # ניתן להוסיף כאן לוגיקה נוספת עבור סוגי פיזיקה ספציפיים למצבים אחרים
            # לדוגמה, אם יש לך מצב 'attack' עם פיזיקה משלו:
            # elif state_name == "attack":
            #     physics_type_determined_by_state_name = "AttackPhysics"
            
            # וודא שסקציית 'physics' קיימת ב-cfg
            if "physics" not in cfg:
                cfg["physics"] = {}
            
            # הוסף/עדכן את ה-'type' לסקציית ה-'physics' בתוך ה-cfg
            cfg["physics"]["type"] = physics_type_determined_by_state_name
            # --- END FIX ---
            
            # --- START DEBUG (עדכון הדפסת Debug) ---
            print(f"DEBUG_PF_1: Loaded config for '{state_name}' from '{state_cfg_path}'. Modified cfg with type: {cfg}")
            physics_section = cfg.get("physics", {})
            print(f"DEBUG_PF_1: Extracted physics section: {physics_section}")
            print(f"DEBUG_PF_1: 'speed_m_per_sec' extracted: {physics_section.get('speed_m_per_sec')}")
            print(f"DEBUG_PF_1: 'next_state_when_finished' extracted: {physics_section.get('next_state_when_finished')}")
            print(f"DEBUG_PF_1: 'type' extracted (after injection): {physics_section.get('type')}")
            # --- END DEBUG ---

            graphics = self.graphics_factory.load(
                sprites_dir=states_dir / state_name / "sprites",
                cfg=cfg
            )
            
            physics = self.physics_factory.create(
                start_cell=(0, 0), 
                cfg=cfg # חשוב שזה יהיה ה-cfg של המצב הספציפי
            )

            state_objects[state_name] = State(
                moves=self.moves_lib[piece_type],
                graphics=graphics,
                physics=physics,
                state_name=state_name,
                next_state_when_finished_name=cfg.get("physics", {}).get("next_state_when_finished")
            )
            logger.debug(f"Created state template '{state_name}' for piece '{piece_type}'.")

        # Stage 2: Link the state templates
        for state_name, state_obj in state_objects.items():
            # 1. Automatic transitions based on physics finish (like move -> long_rest)
            if state_obj._next_state_when_finished_name and \
               state_obj._next_state_when_finished_name in state_objects:
                    transition_event_name = state_obj._next_state_when_finished_name
                
                    state_obj.set_transition(
                    event=transition_event_name,
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
            
            ### START FIX: Add explicit transition for 'move' state to 'long_rest'
            if state_name == "move":
                if "long_rest" in state_objects:
                    state_obj.set_transition(event="long_rest", target=state_objects["long_rest"])
                    logger.debug(f"Template for 'move' explicitly linked transition to 'long_rest'.")
                else:
                    logger.warning(f"Target state 'long_rest' not found for 'move' state's automatic transition in piece type '{piece_type}'.")
            ### END FIX

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
            new_state = copy.deepcopy(state_template) 
            
            new_physics = new_state.get_physics()
            new_physics.board = self.board
            new_physics.cur_pos_m = (
                cell[0] * self.board.cell_W_m,
                cell[1] * self.board.cell_H_m
            )
            new_physics.start_cell = cell 
            
            copied_states[state_name] = new_state
            logger.debug(f"Piece '{p_type}' copied state '{state_name}' initialized physics for cell {cell}.")

        # Re-link the transitions within the copied states to point to other copied states
        for state_name, state_obj in copied_states.items():
            original_template = self.state_templates[p_type][state_name]
            state_obj._transitions = {}
            for event, target_template_state in original_template._transitions.items():
                if target_template_state._state_name in copied_states:
                    state_obj.set_transition(event, copied_states[target_template_state._state_name])
                    logger.debug(f"Piece '{p_type}' copied state '{state_name}' relinked '{event}' to '{target_template_state._state_name}'.")
                else:
                    logger.warning(f"Deep copy transition target '{target_template_state._state_name}' not found for event '{event}' in copied state '{state_name}' of piece '{p_type}'. This transition might be broken.")
            
        initial_state = copied_states.get(initial_state_name)
        if not initial_state:
            raise ValueError(f"Initial state '{initial_state_name}' not found for piece type '{p_type}' in copied states. This indicates a configuration error or deep copy issue.")

        logger.info(f"Initial state '{initial_state_name}' physics for piece '{p_type}' confirmed at starting cell {cell}.")

        for state_obj in copied_states.values():
            state_obj._moves = self.moves_lib[p_type]

        return Piece(
            piece_id=f"{p_type}_{cell[0]}_{cell[1]}",
            init_state=initial_state
        )