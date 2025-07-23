# implementation/img.py
import cv2
import numpy as np
import pathlib
from typing import Optional, Tuple

class Img:
    def __init__(self):
        self.img: Optional[np.ndarray] = None

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        """Reads an image from a given path and optionally resizes it."""
        if not path.exists():
            raise FileNotFoundError(f"Image file not found at {path}")
        self.img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise ValueError(f"Could not read image from {path}. Check file format or corruption.")
        
        if self.img.shape[2] == 3:
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
        elif self.img.shape[2] == 4:
            pass
        else:
            raise ValueError(f"Unsupported image channel count: {self.img.shape[2]}")

        if target_size:
            self.resize(target_size[0], target_size[1])
        
        return self # חשוב להחזיר self כדי לאפשר שרשור (כמו Img().read(...))

    def copy(self) -> 'Img': # שינוי: מ-clone ל-copy
        """Creates a deep copy of the Img object."""
        new_img_obj = Img()
        if self.img is not None:
            new_img_obj.img = self.img.copy() # העתקה עמוקה של מערך ה-numpy
        return new_img_obj

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        """Draws this image onto another Img object at specified coordinates with alpha blending."""
        if self.img is None or other_img.img is None:
            return

        h_src, w_src, _ = self.img.shape
        h_dst, w_dst, _ = other_img.img.shape

        x_dst_start = max(0, x)
        y_dst_start = max(0, y)
        x_dst_end = min(w_dst, x + w_src)
        y_dst_end = min(h_dst, y + h_src)

        x_src_start = x_dst_start - x
        y_src_start = y_dst_start - y
        x_src_end = x_src_start + (x_dst_end - x_dst_start)
        y_src_end = y_src_start + (y_dst_end - y_dst_start)

        if x_dst_start >= x_dst_end or y_dst_start >= y_dst_end:
            return

        roi_dst = other_img.img[y_dst_start:y_dst_end, x_dst_start:x_dst_end]
        roi_src = self.img[y_src_start:y_src_end, x_src_start:x_src_end]

        alpha_src_channel = roi_src[:, :, 3] / 255.0
        alpha_src_blended = alpha_src_channel * alpha
        alpha_dst_blended = 1.0 - alpha_src_blended

        for c in range(0, 3):
            roi_dst[:, :, c] = (alpha_src_blended * roi_src[:, :, c] +
                                 alpha_dst_blended * roi_dst[:, :, c])

    def resize(self, new_width: int, new_height: int):
        """Resizes the image to the specified new_width and new_height."""
        if self.img is None:
            raise ValueError("Cannot resize empty image. 'img' attribute is None.")
        
        current_height, current_width = self.img.shape[:2]
        if new_width == current_width and new_height == current_height:
            return

        interpolation = cv2.INTER_AREA if (new_width < current_width or new_height < current_height) else cv2.INTER_LINEAR
        self.img = cv2.resize(self.img, (new_width, new_height), interpolation=interpolation)

    def get_width(self) -> int: 
        return self.img.shape[1] if self.img is not None else 0
    
    def get_height(self) -> int: 
        return self.img.shape[0] if self.img is not None else 0

    def put_text(self, txt: str, x: int, y: int, font_size: float, *args, **kwargs):
        # בדרך כלל CV2.putText דורש תמונה, אז נדמה זאת
        # (זה רק ב-Img האמיתי, ב-MockImg זה יתועד)
        pass 

    def show(self):
        # בדרך כלל CV2.imshow, נדמה זאת
        pass