import cv2
import numpy as np
from typing import List, Dict, Tuple, Any

from implementation.publish_subscribe.utils import to_chess_notation

from .event_manager import EventManager, EventType # נניח ש-pubsub.py נמצא בתיקיית הבסיס או נגיש

# קבועים עבור ניקוד כלים (כדי ש-MoveLoggerDisplay ידע לחשב)
# אלה יכולים להיות גם מנוהלים בקלאס Game אם תרצה לוגיקה מרוכזת יותר
PIECE_SCORES = {
    "Pawn": 1,
    "Knight": 3,
    "Bishop": 3,
    "Rook": 5,
    "Queen": 9,
    "King": 0 # מלך לא מעניק נקודות בהכאה, אלא מסמל סיום משחק
}

class MoveLoggerDisplay:
    """
    מחלקה האחראית על ניהול והצגת טבלת מהלכים וניקוד על גבי המסך.
    """
    def __init__(self, event_manager: EventManager, font_path: str = None):
        self.event_manager = event_manager
        
        # היסטוריית מהלכים
        # רשימה של מילונים, כל מילון מייצג תור
        # לדוגמה: [{"white_move": "e2-e4 (Pawn)", "black_move": None, "white_score": 0, "black_score": 0}]
        self.moves_history: List[Dict[str, Any]] = []
        self.current_turn_number = 1
        self.white_score = 0
        self.black_score = 0
        self.current_turn_data: Dict[str, Any] = {"white_move": None, "black_move": None}

        # הגדרות תצוגה
        self.font = cv2.FONT_HERSHEY_SIMPLEX # פונט ברירת מחדל
        self.font_scale = 0.6
        self.font_thickness = 1
        self.text_color = (255, 255, 255) # לבן (BGR)
        self.highlight_color = (0, 255, 255) # צהוב-טורקיז (למהלך האחרון)

        # רשימה של שמות כלים (נניח שמות קנוניים שמתקבלים מה-Piece)
        self.piece_names = {
            "pawn": "Pawn", "knight": "Knight", "bishop": "Bishop",
            "rook": "Rook", "queen": "Queen", "king": "King"
        }

        # הרשמה לאירועים רלוונטיים
        self.event_manager.subscribe(EventType.PIECE_MOVED, self._on_piece_moved)
        self.event_manager.subscribe(EventType.PIECE_CAPTURED, self._on_piece_captured)
        self.event_manager.subscribe(EventType.GAME_START, self._on_game_start)


    def _on_game_start(self):
        """מאפס את היסטוריית המהלכים בתחילת משחק חדש."""
        self.moves_history = []
        self.current_turn_number = 1
        self.white_score = 0
        self.black_score = 0
        self.current_turn_data = {"white_move": None, "black_move": None}
        print("MoveLoggerDisplay: Game started, history reset.") # לצרכי דיבוג


    def _on_piece_moved(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        """
        מטפל באירוע תזוזת כלי.
        piece_color: 'white'/'black'
        piece_type: 'pawn', 'knight' וכו'
        from_coords: (row, col)
        to_coords: (row, col)
        """
        move_desc = self._format_move(piece_type, from_coords, to_coords, move_type="Move")
        if piece_color == 'white':
            self.current_turn_data["white_move"] = move_desc
        else:
            self.current_turn_data["black_move"] = move_desc
        # print(f"MoveLoggerDisplay: Piece moved - {move_desc} by {piece_color}") # לצרכי דיבוג


    def _on_piece_captured(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], captured_piece_type: str, captured_piece_color: str):
        """
        מטפל באירוע הכאת כלי.
        piece_color: צבע הכלי שמבצע את ההכאה
        piece_type: סוג הכלי שמבצע את ההכאה
        captured_piece_type: סוג הכלי שהוכה
        captured_piece_color: צבע הכלי שהוכה
        """
        move_desc = self._format_move(piece_type, from_coords, to_coords, move_type="Capture", captured_type=captured_piece_type)

        # הוסף ניקוד לשחקן שמבצע את ההכאה
        score_gained = PIECE_SCORES.get(self.piece_names.get(captured_piece_type.lower(), "Unknown"), 0)

        if piece_color == 'white':
            self.current_turn_data["white_move"] = move_desc
            self.white_score += score_gained
        else:
            self.current_turn_data["black_move"] = move_desc
            self.black_score += score_gained
        # print(f"MoveLoggerDisplay: Piece captured - {move_desc} by {piece_color}. Score gained: {score_gained}") # לצרכי דיבוג


    

    def _format_move(self, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], move_type: str, captured_type: str = None) -> str:
        """
        ממיר קואורדינטות בפורמט (row, col) לפורמט שחמט (e.g., 'a1').
        """


        from_notation = to_chess_notation(from_coords[0], from_coords[1])
        to_notation = to_chess_notation(to_coords[0], to_coords[1])

        formatted_piece_name = self.piece_names.get(piece_type.lower(), piece_type.capitalize())

        if move_type == "Capture" and captured_type:
            captured_formatted_name = self.piece_names.get(captured_type.lower(), captured_type.capitalize())
            return f"{formatted_piece_name} {from_notation}-{to_notation} (x{captured_formatted_name})"
        else:
            return f"{formatted_piece_name} {from_notation}-{to_notation} ({move_type})"


    def draw(self, display_img: np.ndarray, display_width: int, display_height: int):
        """
        מצייר את טבלת המהלכים והניקוד על גבי התמונה הנתונה.
        display_img: ה-NumPy array של תמונת התצוגה שעליה נצייר (לא אובייקט Img).
        display_width: רוחב התצוגה בפיקסלים.
        display_height: גובה התצוגה בפיקסלים.
        """
        # חישוב אזורים לטבלאות (שמאל וימין, עם מרווח מהלוח ומהקצוות)
        # נניח שהלוח ממורכז, ושהטבלאות צריכות להיות משני צידיו

        # נשתמש ב-BOARD_X_OFFSET ו-SCALED_BOARD_WIDTH/HEIGHT שחושבו ב-main.py
        # אבל לשם כך, הפונקציה הזו צריכה לקבל אותם או שהם יהיו חלק מ-MoveLoggerDisplay
        # כרגע, נשתמש בחישוב כללי (צריך להתאים את זה ב-main.py בהמשך)

        # נקודת התחלה כללית לטקסט
        start_y = 50 # מרווח עליון

        # עמודת מהלכים לבנים (צד שמאל)
        white_col_x_start = 20 # מרווח שמאלי
        white_col_width = int((display_width / 2) - 100) # רוחב עמודה לבנה (לפי חצי מסך פחות רווח מהמרכז)
        
        # עמודת מהלכים שחורים (צד ימין)
        black_col_x_start = display_width - white_col_width - 20 # מרווח ימני
        
        # כותרות ניקוד
        score_y_pos = start_y - 20 # קצת מעל טבלת המהלכים
        cv2.putText(display_img, f"White Score: {self.white_score}", (white_col_x_start, score_y_pos), self.font, self.font_scale, self.text_color, self.font_thickness, cv2.LINE_AA)
        cv2.putText(display_img, f"Black Score: {self.black_score}", (black_col_x_start, score_y_pos), self.font, self.font_scale, self.text_color, self.font_thickness, cv2.LINE_AA)


        current_y_white = start_y
        current_y_black = start_y

        # לולאה על היסטוריית המהלכים
        # נציג רק את מספר המהלכים האחרונים שיתאימו למסך
        max_moves_to_display = int((display_height - start_y) / (self.font_scale * 30)) # הערכה גסה
        
        moves_to_show = self.moves_history[-max_moves_to_display:] if len(self.moves_history) > max_moves_to_display else self.moves_history

        for i, turn_data in enumerate(moves_to_show):
            turn_number = turn_data["turn"]
            white_move = turn_data["white_move"]
            black_move = turn_data["black_move"]

            # אם זה המהלך האחרון שהוצג, נדגיש אותו
            is_last_move = (i == len(moves_to_show) - 1)

            # הצגת מהלך לבן
            if white_move:
                text = f"{turn_number}. {white_move}"
                text_color = self.highlight_color if is_last_move else self.text_color
                cv2.putText(display_img, text, (white_col_x_start, current_y_white), self.font, self.font_scale, text_color, self.font_thickness, cv2.LINE_AA)
                current_y_white += int(self.font_scale * 25) # רווח בין שורות

            # הצגת מהלך שחור
            if black_move:
                text = f"{turn_number}. {black_move}"
                text_color = self.highlight_color if is_last_move else self.text_color
                # נמקם את הטקסט של שחור בימין המסך
                # נחשב את רוחב הטקסט כדי למקם אותו בצד ימין
                (text_width, text_height), baseline = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)
                cv2.putText(display_img, text, (display_width - text_width - 20, current_y_black), self.font, self.font_scale, text_color, self.font_thickness, cv2.LINE_AA)
                current_y_black += int(self.font_scale * 25)

        # אם יש מהלך חלקי בתור הנוכחי (לדוגמה, לבן שיחק אבל שחור עדיין לא)
        # נציג אותו גם, אבל ללא מספר תור רשמי
        if self.current_turn_data["white_move"] and not self.current_turn_data["black_move"]:
            text = f"{self.current_turn_number}. {self.current_turn_data['white_move']}"
            cv2.putText(display_img, text, (white_col_x_start, current_y_white), self.font, self.font_scale, self.highlight_color, self.font_thickness, cv2.LINE_AA)
            current_y_white += int(self.font_scale * 25)
        elif self.current_turn_data["black_move"] and not self.current_turn_data["white_move"]:
            text = f"{self.current_turn_number}. {self.current_turn_data['black_move']}"
            (text_width, text_height), baseline = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)
            cv2.putText(display_img, text, (display_width - text_width - 20, current_y_black), self.font, self.font_scale, self.highlight_color, self.font_thickness, cv2.LINE_AA)
            current_y_black += int(self.font_scale * 25)


# פונקציית עזר להמרת קואורדינטות:
# זוהי פונקציה שעוזרת להמיר (row, col) של הלוח לקואורדינטות שחמט סטנדרטיות (a1, e4 וכו').
# נניח ששורות בלוח הן 0-7 מלמעלה למטה, ועמודות 0-7 משמאל לימין.
# בשחמט, 'a' היא העמודה השמאלית, '1' היא השורה התחתונה.
# אז row 0 = rank 8, row 7 = rank 1. col 0 = file 'a', col 7 = file 'h'.
# לדוגמה: (0,0) -> a8, (7,7) -> h1.
def _to_chess_notation(row: int, col: int) -> str:
    file = chr(ord('a') + col)
    rank = str(8 - row) # שורות נספרות מ-0 (למעלה) ב-OpenCV, בשחמט 1-8 (מלמטה)
    return f"{file}{rank}"

