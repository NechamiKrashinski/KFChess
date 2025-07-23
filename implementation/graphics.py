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
        """
        יוצרת העתקה עמוקה של אובייקט Graphics זה.
        מעתיקה את כל המאפיינים, ובמיוחד את רשימת ה-sprites באופן עמוק.
        """
        # יוצרים מופע Graphics חדש עם אותם פרמטרים בסיסיים
        # חשוב שגם ה-board יהיה עותק, ולא הפניה לאותו אובייקט
        # נניח שלמחלקה Board יש מתודת clone() או copy() משלה
        new_board = self.board.clone() # או self.board.clone() אם זו המתודה הקיימת

        new_graphics = Graphics(
            sprites_folder=self.sprites_folder, # pathlib.Path הוא immutable, אז לא צריך deepcopy
            board=new_board,
            loop=self.loop,
            fps=self.fps
        )

        # מעתיקים את מצבי האנימציה
        new_graphics.cur_index = self.cur_index
        new_graphics.last_frame_time = self.last_frame_time
        new_graphics.total_frames = self.total_frames # total_frames הוא רק מספר, לא צריך deepcopy

        # החלק הקריטי: העתקה עמוקה של רשימת ה-sprites
        new_sprites: List[Img] = []
        for sprite in self.sprites:
            # כאן אנחנו קוראים למתודת ה-copy() של כל אובייקט Img/MockImg
            # וזו המתודה שבה וידאנו שיש self.img.copy() בתוך MockImg
            new_sprites.append(sprite.copy()) # ודא שזו המתודה שאתה רוצה שתופעל (copy או clone)
                                            # אם ב-MockImg קראת לה clone, שנה לכאן ל-sprite.clone()
        new_graphics.sprites = new_sprites

        return new_graphics


    def reset(self, cmd: Command):
        """Reset animation state (start from frame 0)."""
        self.cur_index = 0
        self.last_frame_time = cmd.timestamp

    def update(self, now_ms: int):
        """Advance animation frame based on elapsed time."""
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
        """Return the current sprite image."""
        return self.sprites[self.cur_index]
