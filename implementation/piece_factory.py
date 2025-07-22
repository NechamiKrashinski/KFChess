import pathlib
from typing import Dict, Tuple, List
import json
import copy

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
            state_names = main_cfg.get("states", [])
            
            if initial_state_name and state_names:
                state_machine = self._build_state_machine(
                    piece_dir=piece_dir,
                    piece_type=piece_type,
                    initial_state_name=initial_state_name,
                    state_names=state_names
                )
                if state_machine:
                    self.state_machines[piece_type] = state_machine

    def _build_state_machine(self,
                             piece_dir: pathlib.Path,
                             piece_type: str,
                             initial_state_name: str,
                             state_names: List[str]) -> State:
        """
        Builds a state machine for a piece from its directory.
        """
        states_dir = piece_dir / "states"
        state_objects: Dict[str, State] = {}
        
        # Stage 1: Create all State objects
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
            # Create a placeholder physics object. The real position is set in create_piece.
            physics = self.physics_factory.create(
                start_cell=(0, 0),
                cfg=cfg
            )

            state_objects[state_name] = State(
                moves=self.moves_lib[piece_type],
                graphics=graphics,
                physics=physics
            )
            print(f"[DEBUG] Created state '{state_name}' for piece '{piece_type}' with graphics and physics.")

        # Stage 2: Link the states based on config
        for state_name, state_obj in state_objects.items():
            state_cfg_path = states_dir / state_name / "config.json"
            with open(state_cfg_path, 'r') as f:
                cfg = json.load(f)
            
            next_state_name = cfg.get("physics", {}).get("next_state_when_finished")
            if next_state_name and next_state_name in state_objects:
                current_state_obj = state_objects[state_name]
                next_state_obj = state_objects[next_state_name]
                
                # Use the command_type from the physics config as the event
                command_type = cfg.get("physics", {}).get("command_type", next_state_name)
                current_state_obj.set_transition(
                    event=command_type,
                    target=next_state_obj
                )
        
        return state_objects.get(initial_state_name)

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """
        Create a piece of the specified type at the given cell.
        """
        if p_type not in self.state_machines:
            raise ValueError(f"Piece type '{p_type}' not found.")

        # Create a deep copy of the state machine template
        initial_state = copy.deepcopy(self.state_machines[p_type])
        
        # Update the initial position on the physics object of the copied state
        initial_physics = initial_state.get_physics()
        print(f"Type of initial_physics: {type(initial_physics)}")

        initial_physics.cur_pos_m = (
            cell[0] * self.board.cell_W_m,
            cell[1] * self.board.cell_H_m
        )
        
        return Piece(
            piece_id=f"{p_type}_{cell[0]}_{cell[1]}",
            init_state=initial_state
        )