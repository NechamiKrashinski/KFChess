import pathlib
import time
import copy
from typing import Optional, List
from .command import Command
from .board import Board
from .img import Img # Ensure this import is correct

class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        """
        Initialize graphics with sprite directory, board, loop setting, and FPS.
        """
        self.sprites_folder = sprites_folder
        self.board = board
        self.loop = loop
        self.fps = fps

        self.sprites: list[Img] = []
        self.cur_index = 0
        self.last_frame_time: Optional[int] = None
        self.total_frames = 0

        self._load_sprites()

    def _load_sprites(self):
        """
        Load all PNG sprites from the sprites folder, sorted by filename.
        """
        files = sorted(self.sprites_folder.glob("*.png"))
        
        target_size = (self.board.cell_W_pix, self.board.cell_H_pix)

        for file in files:
            img = Img()
            img.read(file, target_size=target_size) # This is where the resize happens now
            self.sprites.append(img)

        self.total_frames = len(self.sprites)
        if self.total_frames == 0:
            raise ValueError(f"No sprites found in: {self.sprites_folder}")

    def copy(self):
        """
        Create a deep copy of this Graphics object.
        """
        # Note: deepcopy for Img objects within sprites list will call Img.clone()
        # if you implement __deepcopy__ in Img. Otherwise, it will just copy references.
        # If Img objects are truly immutable after creation, copying references is fine.
        # If Img can be modified *after* being loaded into Graphics, then Img.clone()
        # needs to be properly handled by deepcopy.
        return copy.deepcopy(self)

    def reset(self, cmd: Command):
        """ 
        Reset animation state (start from frame 0).
        """
        self.cur_index = 0
        self.last_frame_time = cmd.timestamp

    def update(self, now_ms: int):
        """
        Advance animation frame based on elapsed time.
        """
        if self.last_frame_time is None:
            self.last_frame_time = now_ms
            return

        elapsed_ms = now_ms - self.last_frame_time
        frames_to_advance = int(elapsed_ms / (1000 / self.fps))

        if frames_to_advance > 0:
            self.cur_index += frames_to_advance
            if self.loop:
                self.cur_index %= self.total_frames
            else:
                self.cur_index = min(self.cur_index, self.total_frames - 1)

            self.last_frame_time = now_ms

    def get_img(self) -> Img:
        """
        Return the current sprite image.
        """
        return self.sprites[self.cur_index]