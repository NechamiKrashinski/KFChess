import cv2
import numpy as np
import pathlib
from typing import Optional, Tuple

class Img:
    def __init__(self):
        self.img: Optional[np.ndarray] = None

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        """
        Reads an image from a given path and optionally resizes it.
        :param path: Path to the image file.
        :param target_size: Optional tuple (width, height) to resize the image to.
        """
        if not path.exists():
            raise FileNotFoundError(f"Image file not found at {path}")
        self.img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise ValueError(f"Could not read image from {path}. Check file format or corruption.")
        
        # Ensure image has an alpha channel for transparency
        if self.img.shape[2] == 3: # If BGR, convert to BGRA
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
        elif self.img.shape[2] == 4: # Already BGRA
            pass
        else:
            # Handle cases like grayscale or other channel counts if necessary, 
            # or raise an error for unsupported formats.
            raise ValueError(f"Unsupported image channel count: {self.img.shape[2]}")

        if target_size:
            self.resize(target_size[0], target_size[1])

    def clone(self):
        """Creates a deep copy of the Img object."""
        new_img_obj = Img()
        if self.img is not None:
            new_img_obj.img = self.img.copy()
        return new_img_obj

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        """Draws this image onto another Img object at specified coordinates with alpha blending."""
        if self.img is None or other_img.img is None:
            return

        h_src, w_src, _ = self.img.shape  # Source image dimensions
        h_dst, w_dst, _ = other_img.img.shape # Destination image dimensions

        # Calculate the intersection rectangle in destination coordinates
        # These are the coordinates on the *destination* image where we will draw
        x_dst_start = max(0, x)
        y_dst_start = max(0, y)
        x_dst_end = min(w_dst, x + w_src)
        y_dst_end = min(h_dst, y + h_src)

        # Calculate the corresponding coordinates in source image
        # These are the coordinates on the *source* image from which we will read
        x_src_start = x_dst_start - x
        y_src_start = y_dst_start - y
        x_src_end = x_src_start + (x_dst_end - x_dst_start)
        y_src_end = y_src_start + (y_dst_end - y_dst_start)
        # הוסף את השורות הבאות כדי לראות את אזורי החיתוך המחושבים:
        # print(f"DEBUG: Dst Clip: ({x_dst_start},{y_dst_start}) to ({x_dst_end},{y_dst_end})")
        # print(f"DEBUG: Src Clip: ({x_src_start},{y_src_start}) to ({x_src_end},{y_src_end})")

        # Ensure we have a valid region to draw (width and height must be positive)
        if x_dst_start >= x_dst_end or y_dst_start >= y_dst_end:
            # print(f"DEBUG: No valid drawing region for draw_on at ({x}, {y}). "
            #   f"Src size: ({w_src}x{h_src}). Dst size: ({w_dst}x{h_dst}). "
            #   f"Dst Clip: ({x_dst_start},{y_dst_start})-({x_dst_end},{y_dst_end}). "
            #   f"Src Clip: ({x_src_start},{y_src_start})-({x_src_end},{y_src_end})")
            return

        # Get the region of interest (ROI) on the destination image
        roi_dst = other_img.img[y_dst_start:y_dst_end, x_dst_start:x_dst_end]
        
        # Get the corresponding region from the source image
        roi_src = self.img[y_src_start:y_src_end, x_src_start:x_src_end]

        # Alpha blending
        # Extract alpha channel from the source ROI and normalize to 0-1
        alpha_src_channel = roi_src[:, :, 3] / 255.0
        # Apply the global alpha multiplier
        alpha_src_blended = alpha_src_channel * alpha
        # Calculate the inverse alpha for the background
        alpha_dst_blended = 1.0 - alpha_src_blended

        # Perform alpha blending for each color channel (B, G, R)
        for c in range(0, 3): # Iterate over B, G, R channels
            roi_dst[:, :, c] = (alpha_src_blended * roi_src[:, :, c] +
                                alpha_dst_blended * roi_dst[:, :, c])
            
        # Optional: update the alpha channel of the destination if needed for subsequent blending
        # For a simple game board, this might not be necessary if the board is always opaque.
        # If the board can have transparent areas and you want the piece's transparency to affect it:
        # roi_dst[:, :, 3] = (alpha_src_channel * roi_src[:, :, 3] + (1 - alpha_src_channel) * roi_dst[:, :, 3]).astype(np.uint8)

    def resize(self, new_width: int, new_height: int):
        """Resizes the image to the specified new_width and new_height."""
        if self.img is None:
            # It's better to raise an error here if resize is expected to always have an image
            raise ValueError("Cannot resize empty image. 'img' attribute is None.")
        
        current_height, current_width = self.img.shape[:2]
        if new_width == current_width and new_height == current_height:
            return # No resize needed

        # Using INTER_AREA for downsampling (shrinking) and INTER_LINEAR/CUBIC for upsampling (enlarging).
        interpolation = cv2.INTER_AREA if (new_width < current_width or new_height < current_height) else cv2.INTER_LINEAR
        self.img = cv2.resize(self.img, (new_width, new_height), interpolation=interpolation)