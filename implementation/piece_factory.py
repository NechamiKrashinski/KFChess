import pathlib
import json
import copy # שלב 1: הוסף ייבוא למודול copy

from typing import Dict, Tuple, List

from .board import Board
from .graphics_factory import GraphicsFactory
from .moves import Moves
from .physics_factory import PhysicsFactory
from .piece import Piece
from .state import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.moves_lib: Dict[str, Moves] = {}
        self.state_machines: Dict[str, State] = {}
        self.graphics_factory = GraphicsFactory(board=self.board)
        self.physics_factory = PhysicsFactory(board=self.board)
        # שלב 2: תכונה חדשה לאחסון נתוני הקונפיגורציה המלאים של מכונות המצבים
        self._state_machine_config: Dict[str, Dict] = {} 
        self._load_piece_templates()

    def _load_piece_templates(self):
        """
        Loads all piece configurations and state machines from the pieces directory.
        """
        for piece_dir in self.pieces_root.iterdir():
            if not piece_dir.is_dir():
                continue

            piece_type = piece_dir.name
            main_cfg_path = piece_dir / "config.json"
            
            if not main_cfg_path.exists():
                print(f"Warning: No config.json found for piece '{piece_type}'. Skipping.")
                continue

            with open(main_cfg_path, 'r') as f:
                main_cfg = json.load(f)

            # 1. Load moves based on the main config file
            moves_file = main_cfg.get("moves")
            if moves_file:
                moves_path = piece_dir / moves_file
                if moves_path.exists():
                    self.moves_lib[piece_type] = Moves(
                        moves_txt_path=moves_path,
                        dims=(self.board.H_cells, self.board.W_cells)
                    )
                else:
                    print(f"Warning: Moves file not found for piece '{piece_type}' at {moves_path}")
            
            # 2. Build the state machine for the piece
            initial_state_name = main_cfg.get("initial_state")
            # שלב 3: טען את קובץ המעברים המלא עבור סוג הכלי
            state_transitions_path = pathlib.Path(r"C:\Users\user1\Documents\Bootcamp\KFChess\assets\state_transitions.json")

            if not state_transitions_path.exists():
                print(f"Error: states_transitions.json not found for piece '{piece_type}' at {state_transitions_path}")
                continue # דלג על הכלי אם הקובץ חסר

            with open(state_transitions_path, 'r') as f:
                self._state_machine_config[piece_type] = json.load(f) # שמור את כל הקונפיגורציה

            # עכשיו אנו קוראים את שמות המצבים מתוך ה-states_transitions.json
            state_names = list(self._state_machine_config[piece_type].get("states", {}).keys())
            
            if initial_state_name and state_names:
                state_machine = self._build_state_machine(
                    piece_dir=piece_dir,
                    piece_type=piece_type, # העבר את piece_type
                    initial_state_name=initial_state_name,
                    state_names=state_names
                )
                if state_machine:
                    self.state_machines[piece_type] = state_machine

    def _build_state_machine(self,
                             piece_dir: pathlib.Path,
                             piece_type: str, # קבל את piece_type כארגומנט
                             initial_state_name: str,
                             state_names: List[str]) -> State:
        """
        Builds a state machine for a piece from its directory.
        """
        states_dir = piece_dir / "states"
        state_objects: Dict[str, State] = {}
        
        # שלב 4.1: צור את כל אובייקטי ה-State אך ללא קישוריות עדיין
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
            # צור אובייקט פיזיקה. המיקום האמיתי יוגדר ב-create_piece.
            physics = self.physics_factory.create(
                start_cell=(0, 0),
                cfg=cfg,
                state = state_name
            )

            state_objects[state_name] = State(
                moves=self.moves_lib[piece_type],
                graphics=graphics,
                physics=physics,
                state=state_name
            )

        # שלב 4.2: קשר את המצבים ביניהם על בסיס ה-transitions מתוך ה-JSON המלא
        # קבל את הקונפיגורציה המלאה של מכונת המצבים עבור סוג הכלי הנוכחי
        full_state_config = self._state_machine_config.get(piece_type, {}).get("states", {})

        for state_name, state_obj in state_objects.items():
            state_data_from_json = full_state_config.get(state_name)
            if state_data_from_json and "transitions" in state_data_from_json:
                for event, target_state_name in state_data_from_json["transitions"].items():
                    if target_state_name in state_objects:
                        state_obj.set_transition(
                            event=event,
                            target=state_objects[target_state_name]
                        )
                    else:
                        print(f"Warning: Target state '{target_state_name}' for event '{event}' in state '{state_name}' not found for piece type '{piece_type}'.")
            
        return state_objects.get(initial_state_name)

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """
        Create a piece of the specified type at the given cell.
        """
        if p_type not in self.state_machines:
            raise ValueError(f"Piece type '{p_type}' not found.")

        # צור עותק עמוק של תבנית מכונת המצבים, כולל כל המצבים והקישורים ביניהם
        # חשוב להשתמש ב-deepcopy כדי לוודא שכל מופע של כלי מקבל מכונת מצבים נפרדת
        # ולא הפניה לאותה מכונה משותפת.
        initial_state = copy.deepcopy(self.state_machines[p_type])
        
        # עדכן את המיקום ההתחלתי על אובייקט הפיזיקה של המצב שהועתק
        initial_physics = initial_state.get_physics()

        initial_physics.cur_pos_m = (
            cell[0] * self.board.cell_W_m,
            cell[1] * self.board.cell_H_m
        )
        # עדכן גם את start_cell כדי שהתנועה תתחיל מהתא הנכון
        initial_physics.start_cell = cell
        
        return Piece(
            piece_id=f"{p_type}_{cell[0]}_{cell[1]}",
            init_state=initial_state
        )