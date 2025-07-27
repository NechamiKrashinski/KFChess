import numpy as np
import pathlib
from typing import Optional, Tuple, Any

from .img import Img 

class MockImg(Img):
    _read_calls: list = []
    traj: list[tuple[int, int]] = []
    txt_traj: list[tuple[tuple[int, int], str]] = []
    _instance_counter = 0

    def __init__(self):
        super().__init__() 
        self.img: Optional[np.ndarray] = None 
        MockImg._instance_counter += 1
        self._instance_id = MockImg._instance_counter
        print(f"MockImg __init__ called. Instance ID: {self._instance_id}")

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        print(f"MockImg {self._instance_id} read called for path: {path}")
        
        effective_target_size = target_size if target_size is not None else (50, 50) 
        
        self.img = np.copy(np.zeros((effective_target_size[1], effective_target_size[0], 4), dtype=np.uint8))
        print(f"MockImg {self._instance_id} img after read: id={id(self.img)}, shape={self.img.shape}")
        MockImg._read_calls.append({'path': path, 'target_size': target_size})
        return self

    def copy(self) -> 'MockImg':
        print(f"MockImg {self._instance_id} copy called.")
        new_copy = MockImg() 
        if self.img is not None:
            new_copy.img = np.copy(self.img)
            print(f"MockImg {self._instance_id} original img id={id(self.img)}")
            print(f"MockImg {new_copy._instance_id} copied img id={id(new_copy.img)}")
        return new_copy

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        if self.img is None:
            raise ValueError("Cannot draw: current image is not loaded.")
        if other_img.img is None:
            raise ValueError("Cannot draw on: target image is not loaded.")
        if not (0.0 <= alpha <= 1.0):
            raise ValueError("Alpha must be between 0.0 and 1.0.")

        MockImg.traj.append((x, y))

    def put_text(self, txt: str, x: int, y: int, font_size: float, *args, **kwargs):
        MockImg.txt_traj.append(((x, y), txt))

    def show(self):
        pass

    def resize(self, new_width: int, new_height: int):
        if self.img is None:
            raise ValueError("Cannot resize: no image has been loaded yet.")
        if new_width <= 0 or new_height <= 0:
            raise ValueError("New width and height must be positive.")
            
        self.img = np.zeros((new_height, new_width, 4), dtype=np.uint8)

    def get_width(self) -> int:
        return self.img.shape[1] if self.img is not None else 0
    
    def get_height(self) -> int:
        return self.img.shape[0] if self.img is not None else 0

    @classmethod
    def reset(cls):
        print("MockImg.reset() called.")
        cls._read_calls = []
        cls.traj.clear()
        cls.txt_traj.clear()
        cls._instance_counter = 0
    
    @classmethod
    def get_read_calls(cls) -> list:
        return cls._read_calls

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MockImg):
            return NotImplemented
        if self.img is None and other.img is None:
            return True
        if self.img is None or other.img is None:
            return False
        return np.array_equal(self.img, other.img)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __repr__(self) -> str:
        if self.img is not None:
            return f"MockImg(shape={self.img.shape})"
        return "MockImg(uninitialized)"