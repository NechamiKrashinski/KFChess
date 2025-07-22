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
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if self.img.shape[2] == 3:
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
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

    def draw_on(self, other_img, x, y, alpha=1.0):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W:
            print("Warning: Image drawing exceeds board dimensions.")
            return

        roi = other_img.img[y:y + h, x:x + w]
        
        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a.astype(float) / 255.0
            
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            roi[:] = self.img

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
        new_instance = Img()
        if self.img is not None:
            new_instance.img = self.img.copy()
        return new_instance
