import cv2
import numpy as np
import time
from typing import Tuple

from .event_manager import EventManager, EventType

class MessageDisplay:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.current_message: str = ""
        self.message_display_start_time_ms: int = 0
        self.message_duration_ms: int = 3000

        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.font_scale = 1.2
        self.font_thickness = 3
        self.text_color = (0, 255, 0)
        self.upscale_factor = 3

        self.event_manager.subscribe(EventType.GAME_START, self._on_game_start)
        self.event_manager.subscribe(EventType.GAME_END, self._on_game_end)

    def _on_game_start(self, game_time_ms: int):
        self.current_message = "Welcome to Chess! Good luck!"
        self.message_display_start_time_ms = game_time_ms
        print(f"GameMessageDisplay: Game started event received. Displaying: '{self.current_message}'")

    def _on_game_end(self, winner: str, game_time_ms: int): # ודא ש-game_time_ms כלול כאן
        """מטפל באירוע סיום המשחק ומגדיר הודעה."""
        if winner == 'draw':
            self.current_message = "Game Over! It's a DRAW!"
        elif winner == 'white':
            self.current_message = "Game Over! White Wins!"
        elif winner == 'black':
            self.current_message = "Game Over! Black Wins!"
        else:
            self.current_message = "Game Over!"

        # זה התיקון הקריטי: השתמש ב-game_time_ms שהתקבל כפרמטר
        self.message_display_start_time_ms = game_time_ms 
        self.message_duration_ms = 5000 # אולי נרצה שהודעת סיום תוצג יותר זמן
        print(f"GameMessageDisplay: Game ended event received. Displaying: '{self.current_message}'")

        
    def draw(self, display_img: np.ndarray, display_width: int, display_height: int, current_game_time_ms: int):
        if not self.current_message:
            return
        # print(f"DEBUG: MessageDisplay.draw - Message: '{self.current_message}', Current Time: {current_game_time_ms}, Start Time: {self.message_display_start_time_ms}, Duration: {self.message_duration_ms}")
        
        if current_game_time_ms - self.message_display_start_time_ms < self.message_duration_ms:
            text_size = cv2.getTextSize(self.current_message, self.font, self.font_scale, self.font_thickness)
            text_w, text_h = text_size[0]
            
            text_x = (display_width - text_w) // 2
            text_y = display_height // 2 - text_h // 2
            # print(f"DEBUG: MessageDisplay.draw - Calculated text position: ({text_x}, {text_y}), text_w: {text_w}, text_h: {text_h}, Image shape: {display_img.shape}")

            self.draw_sharp_text(display_img, self.current_message, (text_x, text_y),
                                 self.font, self.font_scale, self.text_color, self.font_thickness)
        else:
            self.current_message = ""

    def draw_sharp_text(self, image: np.ndarray, text: str, org_pos: Tuple[int, int],
                        font_face, font_scale: float, color: Tuple[int, int],
                        thickness: int):
        temp_font_scale = font_scale * self.upscale_factor
        temp_font_thickness = thickness * self.upscale_factor

        text_size_info_large = cv2.getTextSize(text, font_face, temp_font_scale, temp_font_thickness)
        text_w_large, text_h_large = text_size_info_large[0]
        baseline_large = text_size_info_large[1] if len(text_size_info_large) > 1 else 0

        # צור קנבס טקסט גדול ב-BGR (3 ערוצים)
        text_canvas_large_bgr = np.zeros((text_h_large + baseline_large, text_w_large, 3), dtype=np.uint8)

        cv2.putText(text_canvas_large_bgr, text, (0, text_h_large),
                            font_face, temp_font_scale, color, temp_font_thickness, cv2.LINE_AA)

        # המר את הקנבס הגדול לגווני אפור וצור את המסכה ממנו
        gray_text_canvas_large = cv2.cvtColor(text_canvas_large_bgr, cv2.COLOR_BGR2GRAY)
        _, alpha_mask_large = cv2.threshold(gray_text_canvas_large, 1, 255, cv2.THRESH_BINARY)

        alpha_mask_small = cv2.resize(alpha_mask_large, (text_w_large // self.upscale_factor, (text_h_large + baseline_large) // self.upscale_factor),
                                         interpolation=cv2.INTER_LANCZOS4)

        text_canvas_bgr_small = cv2.resize(text_canvas_large_bgr, (text_w_large // self.upscale_factor, (text_h_large + baseline_large) // self.upscale_factor),
                                             interpolation=cv2.INTER_LANCZOS4)

        x, y = org_pos
        text_height = alpha_mask_small.shape[0]
        text_width = alpha_mask_small.shape[1]

        x1_target = max(0, x)
        y1_target = max(0, y - text_height)
        x2_target = min(image.shape[1], x + text_width)
        y2_target = min(image.shape[0], y)

        x1_source = 0 if x >= 0 else -x
        y1_source = 0 if y - text_height >= 0 else -(y - text_height)
        x2_source = text_width if x + text_width <= image.shape[1] else image.shape[1] - x
        y2_source = text_height if y <= image.shape[0] else image.shape[0] - (y - text_height)

        # הסר את הדפסות הדאג המיותרות
        # print(f"DEBUG: draw_sharp_text - org_pos: {org_pos}, text_width: {text_width}, text_height: {text_height}")
        # print(f"DEBUG: draw_sharp_text - Target ROI (y1:y2, x1:x2): ({y1_target}:{y2_target}, {x1_target}:{x2_target})")
        # print(f"DEBUG: draw_sharp_text - Source ROI (y1:y2, x1:x2): ({y1_source}:{y2_source}, {x1_source}:{x2_source})")
        # print(f"DEBUG: draw_sharp_text - Input Image shape: {image.shape}")

        if x1_target >= x2_target or y1_target >= y2_target or \
           x1_source >= x2_source or y1_source >= y2_source:
            # print("DEBUG: draw_sharp_text - ROI calculation resulted in empty or invalid region. Skipping draw.")
            return

        roi = image[y1_target:y2_target, x1_target:x2_target]
        text_roi = text_canvas_bgr_small[y1_source:y2_source, x1_source:x2_source]
        mask_roi = alpha_mask_small[y1_source:y2_source, x1_source:x2_source]

        # הסר את הדפסות הדאג המיותרות
        # print(f"DEBUG: draw_sharp_text - Extracted ROI shapes: roi {roi.shape}, text_roi {text_roi.shape}, mask_roi {mask_roi.shape}")

        if roi.shape != text_roi.shape or roi.shape[:2] != mask_roi.shape[:2]:
            # print(f"DEBUG: draw_sharp_text - Shape mismatch: ROI {roi.shape}, text_roi {text_roi.shape}, mask_roi {mask_roi.shape}. Skipping draw.")
            return

        # החזר את לוגיקת שילוב הטקסט המקורית
        mask_inv = cv2.bitwise_not(mask_roi)
        img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        img_fg = cv2.bitwise_and(text_roi, text_roi, mask=mask_roi)
        final_segment = cv2.add(img_bg, img_fg)
        image[y1_target:y2_target, x1_target:x2_target] = final_segment

        