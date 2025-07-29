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

    def _on_game_end(self, winner: str, game_time_ms: int):
        if winner == 'draw':
            self.current_message = "Game Over! It's a DRAW!"
        elif winner == 'white':
            self.current_message = "Game Over! White Wins!"
        elif winner == 'black':
            self.current_message = "Game Over! Black Wins!"
        else:
            self.current_message = "Game Over!"

        self.message_display_start_time_ms = game_time_ms 
        self.message_duration_ms = 5000 
        print(f"GameMessageDisplay: Game ended event received. Displaying: '{self.current_message}'")

        
    def draw(self, display_img: np.ndarray, display_width: int, display_height: int, current_game_time_ms: int):
        if not self.current_message:
            return
        
        if current_game_time_ms - self.message_display_start_time_ms < self.message_duration_ms:
            text_size = cv2.getTextSize(self.current_message, self.font, self.font_scale, self.font_thickness)
            text_w, text_h = text_size[0]
            
            text_x = (display_width - text_w) // 2
            text_y = display_height // 2 - text_h // 2

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

        text_canvas_large_bgr = np.zeros((text_h_large + baseline_large, text_w_large, 3), dtype=np.uint8)

        cv2.putText(text_canvas_large_bgr, text, (0, text_h_large),
                            font_face, temp_font_scale, color, temp_font_thickness, cv2.LINE_AA)

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

        
        if x1_target >= x2_target or y1_target >= y2_target or \
           x1_source >= x2_source or y1_source >= y2_source:
            return

        roi = image[y1_target:y2_target, x1_target:x2_target]
        text_roi = text_canvas_bgr_small[y1_source:y2_source, x1_source:x2_source]
        mask_roi = alpha_mask_small[y1_source:y2_source, x1_source:x2_source]

     
        if roi.shape != text_roi.shape or roi.shape[:2] != mask_roi.shape[:2]:
            return

        mask_inv = cv2.bitwise_not(mask_roi)
        img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        img_fg = cv2.bitwise_and(text_roi, text_roi, mask=mask_roi)
        final_segment = cv2.add(img_bg, img_fg)
        image[y1_target:y2_target, x1_target:x2_target] = final_segment

        