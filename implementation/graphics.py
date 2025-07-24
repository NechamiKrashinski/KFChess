# graphics.py

import pathlib
import time
import copy
from typing import Optional, List
from .command import Command
from .board import Board
from .img import Img

class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        self.sprites_folder = sprites_folder
        self.board = board
        self.loop = loop
        self.fps = fps

        self.sprites: list[Img] = []
        self.cur_index = 0
        self.last_frame_time: Optional[int] = None
        self.total_frames = 0
        self.animation_finished = False

        self._load_sprites() # <-- הקריאה למתודה הזו

    # הוסף את בלוק הקוד הבא חזרה למחלקה Graphics:
    def _load_sprites(self):
        """Load all PNG sprites from the sprites folder, sorted by filename."""
        files = sorted(self.sprites_folder.glob("*.png"))
        
        target_size = (self.board.cell_W_pix, self.board.cell_H_pix)

        for file in files:
            img = Img()
            img.read(file, target_size=target_size)
            self.sprites.append(img)

        self.total_frames = len(self.sprites)
        if self.total_frames == 0:
            raise ValueError(f"No sprites found in: {self.sprites_folder}")

    def copy(self):
        # ... (שאר המתודה copy) ...
        new_board = self.board.clone()

        new_graphics = Graphics(
            sprites_folder=self.sprites_folder,
            board=new_board,
            loop=self.loop,
            fps=self.fps
        )

        new_graphics.cur_index = self.cur_index
        new_graphics.last_frame_time = self.last_frame_time
        new_graphics.total_frames = self.total_frames
        new_graphics.animation_finished = self.animation_finished

        new_sprites: List[Img] = []
        for sprite in self.sprites:
            new_sprites.append(sprite.copy())
        new_graphics.sprites = new_sprites

        return new_graphics

    def reset(self, cmd: Command):
        # ... (שאר המתודה reset) ...
        self.cur_index = 0
        self.last_frame_time = cmd.timestamp
        self.animation_finished = False

    def update(self, now_ms: int) -> Optional[Command]:
        # ... (שאר המתודה update) ...
        if self.animation_finished and not self.loop: 
            return None 

        if self.last_frame_time is None:
            self.last_frame_time = now_ms
            return None

        elapsed_ms = now_ms - self.last_frame_time
        frames_to_advance = int(elapsed_ms / (1000 / self.fps))

        if frames_to_advance > 0:
            self.cur_index += frames_to_advance
            self.last_frame_time = now_ms

            if self.loop:
                self.cur_index %= self.total_frames
                return None
            else:
                if self.cur_index >= self.total_frames:
                    self.cur_index = self.total_frames - 1
                    if not self.animation_finished:
                        self.animation_finished = True
                        print(f"DEBUG: Graphics for {self.sprites_folder.name} finished animation at {now_ms}ms!") # הוסף את השורה הזו
                        return None
        return None
    
    def is_finished(self) -> bool: 
        return self.animation_finished and not self.loop

    def get_img(self) -> Img:
        return self.sprites[self.cur_index]