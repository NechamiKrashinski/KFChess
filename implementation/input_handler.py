# implementation/input_handler.py
from abc import ABC, abstractmethod
from implementation.command import Command
from typing import Optional, Tuple

class InputHandler(ABC):
    @abstractmethod
    def start(self): ...
    
    @abstractmethod
    def get_command(self) -> Optional[Command]: ...
    
    @abstractmethod
    def update_on_key(self, key: int) -> None: ...
    
    @abstractmethod
    def draw_ui(self, draw_fn): ...
