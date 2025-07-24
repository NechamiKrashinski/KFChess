import pathlib
import time # לא נראה שנעשה שימוש ישיר ב-time במחלקה זו, אבל נשאיר אם יש כוונה
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
        self._animation_finished = False # **חדש: דגל פנימי לסיום אנימציה**

        self._load_sprites()

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
        new_graphics._animation_finished = self._animation_finished # **העתק גם את הדגל**

        new_sprites: List['Img'] = []
        for sprite in self.sprites:
            new_sprites.append(sprite.copy())
        new_graphics.sprites = new_sprites

        return new_graphics

    def reset(self, cmd: Optional[Command]): # שיניתי ל-Optional[Command]
        """Reset animation state (start from frame 0)."""
        self.cur_index = 0
        self.last_frame_time = cmd.timestamp if cmd else int(time.time() * 1000) # **שינוי: אם אין קומנד, השתמש בזמן הנוכחי**
        self._animation_finished = False # **איפוס הדגל באיפוס**


    def update(self, now_ms: float):
        # print("[DEBUG] update graphics")
        """Advance animation frame based on elapsed time."""
        if self._animation_finished and not self.loop: # אם סיימה ואינה בלולאה, אל תעדכן
            return

        if self.last_frame_time is None:
            self.last_frame_time = now_ms
            return

        elapsed_ms = now_ms - self.last_frame_time
        
        # חישוב כמה פריימים עברו מאז העדכון האחרון.
        # אם ה-fps הוא 0 (לדוגמה, במצב idle עם פריים בודד), לא נתקדם בפריימים.
        frames_to_advance = 0
        if self.fps > 0:
            frames_to_advance = int(elapsed_ms / (1000 / self.fps))


        if frames_to_advance > 0:
            self.cur_index += frames_to_advance
            if self.loop:
                self.cur_index %= self.total_frames
            else:
                # אם אנחנו לא בלולאה והגענו לסוף, סמן כסיום
                if self.cur_index >= self.total_frames:
                    self.cur_index = self.total_frames - 1
                    self._animation_finished = True # **סמן שסיימת אנימציה**

            self.last_frame_time = now_ms

    def is_finished(self) -> bool: # **חדש**
        """
        Checks if the non-looping animation has completed.
        For looping animations, this will always return False (unless total_frames is 0).
        """
        if self.loop:
            return False # אנימציה בלולאה לא "נגמרת"
        return self._animation_finished

    def get_img(self) -> Img:
        """Return the current sprite image."""
        if not self.sprites: # הגנה מפני רשימה ריקה
            return Img() # או החזר תמונה ריקה מתאימה
        return self.sprites[self.cur_index]