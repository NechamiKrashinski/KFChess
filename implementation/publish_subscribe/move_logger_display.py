import cv2
import numpy as np
from typing import List, Dict, Tuple, Any

from implementation.publish_subscribe.utils import to_chess_notation 
from .event_manager import EventManager, EventType

PIECE_SCORES = {
    "Pawn": 1,
    "Knight": 3,
    "Bishop": 3,
    "Rook": 5,
    "Queen": 9,
    "King": 0 
}

class MoveLoggerDisplay:
    def __init__(self, event_manager: EventManager, font_path: str = None):
        self.event_manager = event_manager
        
        self.moves_history: List[Dict[str, Any]] = []
        self.white_score = 0
        self.black_score = 0

        self.font = cv2.FONT_HERSHEY_COMPLEX 
        self.font_scale = 1.0 
        self.font_thickness = 2 
        self.text_color = (255, 255, 255) 
        self.highlight_color = (0, 255, 255) 
        self.padding_y = 10 

        self.upscale_factor = 3 

        self.piece_names = {
            "pawn": "Pawn", "knight": "Knight", "bishop": "Bishop",
            "rook": "Rook", "queen": "Queen", "king": "King",
            "p": "Pawn", "n": "Knight", "b": "Bishop", 
            "r": "Rook", "q": "Queen", "k": "King"
        }

        self.event_manager.subscribe(EventType.PIECE_MOVED, self._on_piece_moved)
        self.event_manager.subscribe(EventType.PIECE_CAPTURED, self._on_piece_captured)
        self.event_manager.subscribe(EventType.GAME_START, self._on_game_start)
        self.event_manager.subscribe(EventType.PIECE_JUMPED, self._on_piece_jumped)

    def _on_game_start(self):
        self.moves_history = []
        self.white_score = 0
        self.black_score = 0

    def _on_piece_moved(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        move_desc = self._format_move(piece_type, from_coords, to_coords, move_type="Move")
        self.moves_history.append({"player_color": piece_color, "move_desc": move_desc, "event_type": "move"})

    def _on_piece_captured(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], captured_piece_type: str, captured_piece_color: str):
        move_desc = self._format_move(piece_type, from_coords, to_coords, move_type="Capture", captured_type=captured_piece_type)

        # --- הוסף את השורות הבאות לאבחון ---
        print(f"Captured piece event received:")
        print(f"  captured_piece_type (raw): '{captured_piece_type}'")
        print(f"  captured_piece_type (lower): '{captured_piece_type.lower()}'")
        
        normalized_piece_name = self.piece_names.get(captured_piece_type.lower(), "Unknown")
        print(f"  Normalized piece name: '{normalized_piece_name}'")
        
        score_gained = PIECE_SCORES.get(normalized_piece_name, 0)
        print(f"  Score gained from PIECE_SCORES: {score_gained}")
        # --- סוף הדפסות אבחון ---

        if piece_color.lower() == 'white' or piece_color.lower() == 'w':
            self.white_score += score_gained
            print(f"  White score updated to: {self.white_score}")
        else:
            self.black_score += score_gained
            print(f"  Black score updated to: {self.black_score}")
        
        self.moves_history.append({"player_color": piece_color, "move_desc": move_desc, "event_type": "capture", "score_gained": score_gained})

    def _on_piece_jumped(self, piece_color: str, piece_type: str, cell_coords: Tuple[int, int]):
        cell_notation = to_chess_notation(cell_coords[0], cell_coords[1]) 
        formatted_piece_name = self.piece_names.get(piece_type.lower(), piece_type.capitalize())
        
        move_desc = f"{formatted_piece_name} enters Jump state at {cell_notation}"
        self.moves_history.append({"player_color": piece_color, "move_desc": move_desc, "event_type": "jump"})

    def _format_move(self, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], move_type: str, captured_type: str = None) -> str:
        from_notation = to_chess_notation(from_coords[0], from_coords[1])
        to_notation = to_chess_notation(to_coords[0], to_coords[1])

        formatted_piece_name = self.piece_names.get(piece_type.lower(), piece_type.capitalize())

        if move_type == "Capture" and captured_type:
            captured_formatted_name = self.piece_names.get(captured_type.lower(), captured_type.capitalize())
            return f"{formatted_piece_name} {from_notation}x{to_notation} ({captured_formatted_name})"
        else:
            return f"{formatted_piece_name} {from_notation}-{to_notation}"

    def draw(self, display_img: np.ndarray, display_width: int, display_height: int,
             board_x_offset: int, board_y_offset: int, board_width: int, board_height: int):

        margin = 20
        
        text_size_info_temp = cv2.getTextSize("Lg", self.font, self.font_scale, self.font_thickness)
        temp_w, temp_h_for_line = text_size_info_temp[0]
        line_height = temp_h_for_line + self.padding_y

        # --- הצגת ניקוד ---
        black_score_text = f"Black Score: {self.black_score}"
        score_text_info_black = cv2.getTextSize(black_score_text, self.font, self.font_scale, self.font_thickness)
        black_score_w, black_score_h = score_text_info_black[0]
        # black_score_baseline = score_text_info_black[1] if len(score_text_info_black) > 1 else 0 # אין צורך ישיר בבייסליין כאן

        black_score_x = board_x_offset + (board_width - black_score_w) // 2
        black_score_y = board_y_offset - margin
        if black_score_y - black_score_h < margin:
            black_score_y = margin + black_score_h
        self.draw_sharp_text(display_img, black_score_text, (black_score_x, black_score_y),
                             self.font, self.font_scale, self.text_color, self.font_thickness)

        white_score_text = f"White Score: {self.white_score}"
        score_text_info_white = cv2.getTextSize(white_score_text, self.font, self.font_scale, self.font_thickness)
        white_score_w, white_score_h = score_text_info_white[0]
        # white_score_baseline = score_text_info_white[1] if len(score_text_info_white) > 1 else 0 # אין צורך ישיר בבייסליין כאן

        white_score_x = board_x_offset + (board_width - white_score_w) // 2
        white_score_y = board_y_offset + board_height + margin + white_score_h
        if white_score_y > display_height - margin:
            white_score_y = display_height - margin
        self.draw_sharp_text(display_img, white_score_text, (white_score_x, white_score_y),
                             self.font, self.font_scale, self.text_color, self.font_thickness)

        # --- מיקום היסטוריית מהלכים ---
        # חישוב נקודת ההתחלה האנכית של אזור המהלכים
        # זה אמור להיות מספיק מתחת לניקוד השחור
        # black_score_y היא נקודת הבסיס, אז black_score_y + black_score_baseline הוא התחתית האמיתית של הטקסט
        # נשתמש ב-black_score_y + (black_score_h // 2) + self.padding_y * 2
        # או פשוט נגדיר יחס קבוע ביחס לקצה העליון אם זה עובד טוב יותר מבחינת עיצוב קבוע
        
        # כדי לפשט, נגדיר את זה קבוע מראש, אם זה לא מתנגש עם ניקוד או לוח
        moves_section_start_y = max(margin + line_height * 2, black_score_y + temp_h_for_line + self.padding_y * 2)

        available_height_for_moves = display_height - moves_section_start_y - margin
        max_rows_per_col = int(available_height_for_moves / line_height)
        if max_rows_per_col < 1:
            max_rows_per_col = 1

        white_moves_list = [entry["move_desc"] for entry in self.moves_history if entry["player_color"].lower() in ["white", "w"]]
        black_moves_list = [entry["move_desc"] for entry in self.moves_history if entry["player_color"].lower() in ["black", "b"]]

        # --- עמודת מהלכים לבנים (צד שמאל) ---
        white_col_x_start = margin
        current_y_white = moves_section_start_y

        self.draw_sharp_text(display_img, "White Moves:", (white_col_x_start, current_y_white),
                        self.font, self.font_scale, self.text_color, self.font_thickness)
        current_y_white += line_height

        moves_to_show_white = white_moves_list[-max_rows_per_col:]
        for i, move_desc in enumerate(moves_to_show_white):
            text = f"{len(white_moves_list) - len(moves_to_show_white) + i + 1}. {move_desc}"
            text_color = self.highlight_color if (i == len(moves_to_show_white) - 1 and self.moves_history and self.moves_history[-1]["player_color"].lower() in ["white", "w"]) else self.text_color

            self.draw_sharp_text(display_img, text, (white_col_x_start, current_y_white),
                            self.font, self.font_scale, text_color, self.font_thickness)
            current_y_white += line_height

        # --- עמודת מהלכים שחורים (צד ימין) ---
        black_col_x_start = display_width - margin
        current_y_black = moves_section_start_y

        header_text = "Black Moves:"
        header_text_info = cv2.getTextSize(header_text, self.font, self.font_scale, self.font_thickness)
        header_w, _ = header_text_info[0]

        self.draw_sharp_text(display_img, header_text, (black_col_x_start - header_w, current_y_black),
                        self.font, self.font_scale, self.text_color, self.font_thickness)
        current_y_black += line_height

        moves_to_show_black = black_moves_list[-max_rows_per_col:]
        for i, move_desc in enumerate(moves_to_show_black):
            text = f"{len(black_moves_list) - len(moves_to_show_black) + i + 1}. {move_desc}"
            text_color = self.highlight_color if (i == len(moves_to_show_black) - 1 and self.moves_history and self.moves_history[-1]["player_color"].lower() in ["black", "b"]) else self.text_color

            text_size_info_move = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)
            text_w, _ = text_size_info_move[0] # השתמש ב-text_size_info_move במקום ב-text_size_info_black
            
            self.draw_sharp_text(display_img, text, (display_width - text_w - margin, current_y_black),
                            self.font, self.font_scale, text_color, self.font_thickness)
            current_y_black += line_height

    # --- פונקציית העזר draw_sharp_text (נותרה ללא שינוי) ---
    def draw_sharp_text(self, image: np.ndarray, text: str, org_pos: Tuple[int, int],
                        font_face, font_scale: float, color: Tuple[int, int],
                        thickness: int):

        temp_font_scale = font_scale * self.upscale_factor
        temp_font_thickness = thickness * self.upscale_factor

        text_size_info_large = cv2.getTextSize(text, font_face, temp_font_scale, temp_font_thickness)
        text_w_large, text_h_large = text_size_info_large[0]
        baseline_large = text_size_info_large[1] if len(text_size_info_large) > 1 else 0

        text_canvas_large = np.zeros((text_h_large + baseline_large, text_w_large, 4), dtype=np.uint8)

        cv2.putText(text_canvas_large, text, (0, text_h_large),
                    font_face, temp_font_scale, color, temp_font_thickness, cv2.LINE_AA)

        alpha_channel = text_canvas_large[:,:,0]
        _, alpha_mask_large = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)

        alpha_mask_small = cv2.resize(alpha_mask_large, (text_w_large // self.upscale_factor, (text_h_large + baseline_large) // self.upscale_factor),
                                      interpolation=cv2.INTER_LANCZOS4)

        text_canvas_bgr_small = cv2.resize(text_canvas_large[:,:,:3], (text_w_large // self.upscale_factor, (text_h_large + baseline_large) // self.upscale_factor),
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