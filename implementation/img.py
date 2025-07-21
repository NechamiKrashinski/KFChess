from __future__ import annotations

import pathlib

import cv2
import numpy as np

class Img:
    def __init__(self):
        self.img = None

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        """
        Load `path` into self.img and **optionally resize**.

        Parameters
        ----------
        path : str | Path
            Image file to load.
        size : (width, height) | None
            Target size in pixels.  If None, keep original.
        keep_aspect : bool
            • False  → resize exactly to `size`
            • True   → shrink so the *longer* side fits `size` while
                       preserving aspect ratio (no cropping).
        interpolation : OpenCV flag
            E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

        Returns
        -------
        Img
            `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
        """
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    class Img:
    # ... (שאר הקוד של המחלקה)

        def draw_on(self, other_img, x, y, alpha=1.0):
            """
            Draws this image onto another Img object at a specific position.
            The alpha parameter controls the transparency of the drawn image.
            """
            if self.img is None or other_img.img is None:
                raise ValueError("Both images must be loaded before drawing.")

            h, w = self.img.shape[:2]
            H, W = other_img.img.shape[:2]

            if y + h > H or x + w > W:
                # במקום להעלות שגיאה, נדפיס אזהרה ונתעלם.
                print("Warning: Image drawing exceeds board dimensions.")
                return

            roi = other_img.img[y:y + h, x:x + w]
            
            # שימוש בערוץ האלפא, אם קיים, לשילוב
            if self.img.shape[2] == 4:
                b, g, r, a = cv2.split(self.img)
                mask = a.astype(float) / 255.0
                
                # Blend the piece onto the ROI, using the alpha channel for transparency
                for c in range(3):
                    roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
            else: # אין ערוץ אלפא
                roi[:] = self.img

            # עכשיו, נטפל בשקיפות הכללית עם הפרמטר alpha
            if alpha < 1.0:
                blended = cv2.addWeighted(roi, alpha, roi, 1 - alpha, 0)
                other_img.img[y:y + h, x:x + w] = blended
            else:
                other_img.img[y:y + h, x:x + w] = roi
    
    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def clone(self) -> "Img":
        """
        Creates a new Img instance with a deep copy of the image data.
        """
        new_instance = Img()
        if self.img is not None:
            # .copy() is a NumPy method that creates a new array with the same data
            new_instance.img = self.img.copy()
        return new_instance