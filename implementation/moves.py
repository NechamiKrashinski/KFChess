# moves.py
import pathlib
from typing import List, Tuple, Dict

class Moves:
    def __init__(self, moves_txt_path: pathlib.Path, dims: Tuple[int, int]):
        self.dims = dims
        # שינוי: לא נשמור כאן moves_all גנרי. נגדיר אותו לפי סוג הכלי
        # או נטען קבצי תנועה ספציפיים לכל כלי.
        # לצורך הפתרון הזה, נניח שהקובץ moves_txt_path מכיל את כל הקואורדינטות היחסיות לכל הכלים
        # ו-piece_type יקבע איזה מהן רלוונטיות.
        # נשנה את המבנה לשמירת חוקי תנועה גולמיים לפי סוג:
        self.raw_moves: Dict[str, List[Tuple[int, int, str]]] = self._load_moves(moves_txt_path)


    def _load_moves(self, moves_txt_path: pathlib.Path) -> Dict[str, List[Tuple[int, int, str]]]:
        # זו דרך פשטנית לטעון. בפרויקט גדול יותר, אולי יהיו קבצים נפרדים לכל כלי.
        # לצורך הדימוי, נניח שיש בקובץ סימונים לכלי מסוים.
        # זה דורש שינוי בקובץ moves.txt כדי לכלול את סוג הכלי.
        # למשל: "P:0,1:normal", "P:1,1:capture", "R:0,1:straight"
        
        # לפתרון מהיר, אנו נגדיר את המהלכים באופן קבוע בתוך הקוד לפי סוג כלי.
        # אם אתה רוצה שהם יגיעו מקובץ, תצטרך לשנות את מבנה הקובץ והקונסטרוקטור.
        
        # 💡 אם אתה מתכנן לקרוא את חוקי התנועה מקובץ, תצטרך לפרסר את הקובץ
        # באופן חכם יותר כדי לשייך dx, dy לסוגי כלים.
        # כרגע, לצורך הדימוי, אני אגדיר אותם ידנית פה, כפי שהצעתי מקודם.
        
        # 💡 אם קובץ moves.txt מכיל *רק* את ה-dx,dy הבסיסיים לכל כיוון (למשל, 0,1 ולא 0,5),
        # אז הגישה תהיה שונה. אנו נניח שיש לנו סטים של dx,dy לפי סוג הכלי.
        
        # מכיוון שלא סיפקת את moves.txt, אציג כאן לוגיקה שמניחה שאתה תגדיר את זה
        # בקוד עצמו או שתשנה את אופן קריאת הקובץ.
        
        return {} # לא טוען כלום בשלב זה. הלוגיקה תהיה ב-get_moves

    def get_moves(self,
                  r: int,
                  c: int,
                  all_occupied_cells: List[Tuple[int, int]],
                  occupied_enemy_cells: List[Tuple[int, int]],
                  can_jump: bool, # רק לפרש יהיה True
                  piece_type: str, # לדוגמה: 'P', 'R', 'N', 'B', 'Q', 'K'
                  my_color: str    # 'W' או 'B'
                  ) -> List[Tuple[int, int]]:

        rows, cols = self.dims
        valid_moves: List[Tuple[int, int]] = []
        
        # פונקציית עזר פנימית לבדיקת גבולות
        def _is_valid_cell(cell: Tuple[int, int]) -> bool:
            x, y = cell
            return 0 <= x < rows and 0 <= y < cols

        if piece_type == 'P': # חייל (Pawn)
            direction = -1 if my_color == 'W' else 1 # חייל לבן זז ל-y נמוך יותר, שחור ל-y גבוה יותר

            # 1. תנועה קדימה (תא אחד)
            forward_one_cell = (r, c + direction)
            if _is_valid_cell(forward_one_cell) and forward_one_cell not in all_occupied_cells:
                valid_moves.append(forward_one_cell)

            # 2. תנועה קדימה (שני תאים - רק מהלך ראשון)
            start_row = 6 if my_color == 'W' else 1
            if c == start_row:
                forward_two_cell = (r, c + 2 * direction)
                # ודא שגם התא הראשון וגם התא השני פנויים
                if _is_valid_cell(forward_two_cell) and \
                   forward_one_cell not in all_occupied_cells and \
                   forward_two_cell not in all_occupied_cells:
                    valid_moves.append(forward_two_cell)

            # 3. לכידה אלכסונית
            capture_diag_left = (r - 1, c + direction)
            capture_diag_right = (r + 1, c + direction)

            for target_cell in [capture_diag_left, capture_diag_right]:
                if _is_valid_cell(target_cell) and target_cell in occupied_enemy_cells:
                    valid_moves.append(target_cell)

        elif piece_type == 'N': # פרש (Knight)
            knight_offsets = [
                (1, 2), (1, -2), (-1, 2), (-1, -2),
                (2, 1), (2, -1), (-2, 1), (-2, -1)
            ]
            for dx, dy in knight_offsets:
                target_cell = (r + dx, c + dy)
                if _is_valid_cell(target_cell):
                    if target_cell not in all_occupied_cells: # תא ריק
                        valid_moves.append(target_cell)
                    elif target_cell in occupied_enemy_cells: # כלי אויב
                        valid_moves.append(target_cell)
                    # אין צורך לבדוק חסימות בדרך עבור פרש (can_jump הוא True עבורו)

        elif piece_type in ['R', 'B', 'Q', 'K']: # צריח (Rook), רץ (Bishop), מלכה (Queen), מלך (King)
            # הגדר את הכיוונים הבסיסיים לכל סוג כלי
            directions: List[Tuple[int, int]] = []
            if piece_type == 'R' or piece_type == 'Q': # צריח או מלכה (ישר)
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)]) # ימין, שמאל, למטה, למעלה
            if piece_type == 'B' or piece_type == 'Q': # רץ או מלכה (אלכסון)
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)]) # 4 אלכסונים
            if piece_type == 'K': # מלך (צעד אחד בכל כיוון)
                directions.extend([
                    (0, 1), (0, -1), (1, 0), (-1, 0),  # ישר
                    (1, 1), (1, -1), (-1, 1), (-1, -1) # אלכסון
                ])

            for dr, dc in directions:
                # עבור מלך, רק צעד אחד מותר. עבור אחרים, לולאה
                max_steps = 1 if piece_type == 'K' else max(rows, cols) 

                for i in range(1, max_steps + 1):
                    target_cell = (r + dr * i, c + dc * i)

                    if not _is_valid_cell(target_cell):
                        break # יצאנו מגבולות הלוח, עצור כיוון זה

                    if target_cell in all_occupied_cells:
                        # התא תפוס. אם זה אויב, לוכדים ועוצרים. אם זה ידיד, רק עוצרים.
                        if target_cell in occupied_enemy_cells:
                            valid_moves.append(target_cell) # לכידה חוקית
                        break # בכל מקרה, עוצר את התנועה בכיוון זה

                    else: # התא ריק
                        valid_moves.append(target_cell) # תנועה חוקית

        # הערה: _is_straight_move ו- _is_path_blocked כבר לא נחוצים באותה צורה
        # מכיוון שהלוגיקה החדשה מטפלת בחסימות ישירות.
        return valid_moves

    # _is_straight_move ו- _is_path_blocked כבר לא משמשים בלוגיקה החדשה של get_moves
    # ניתן להסיר או לשמור אותם למטרות דיבוג או שימוש אחר עתידי אם תרצה.
    # אני משאיר אותם כרגע רק כדי שיהיה לך את כל הקוד שלך.
    def _is_straight_move(self, dx: int, dy: int) -> bool:
        """Determines if a move (dx, dy) represents a straight line (horizontal, vertical, or diagonal)."""
        return dx == 0 or dy == 0 or abs(dx) == abs(dy)

    def _is_path_blocked(self,
                          start_cell: Tuple[int, int],
                          end_cell: Tuple[int, int],
                          occupied_cells: List[Tuple[int, int]]) -> bool:
        print(f"DEBUG: Checking path from {start_cell} to {end_cell}")
        print(f"DEBUG: Occupied cells: {occupied_cells}")
            
        start_row, start_col = start_cell
        end_row, end_col = end_cell

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        step_row = 0
        if delta_row > 0:
            step_row = 1
        elif delta_row < 0:
            step_row = -1

        step_col = 0
        if delta_col > 0:
            step_col = 1
        elif delta_col < 0:
            step_col = -1

        # כדי למנוע חסימה של תא היעד עצמו אם הוא מכיל כלי אויב
        # עלינו לוודא שאנחנו לא בודקים את תא היעד כחסימה.
        # steps should go up to, but not include, the end cell
        steps = max(abs(delta_row), abs(delta_col))

        for i in range(1, steps): # Loop only through intermediate cells
            intermediate_row = start_row + i * step_row
            intermediate_col = start_col + i * step_col
            intermediate_cell = (intermediate_row, intermediate_col)
            print(f"DEBUG: Checking intermediate cell: {intermediate_cell}")

            if intermediate_cell in occupied_cells:
                print(f"DEBUG: Path BLOCKED at {intermediate_cell}")
                return True
        print(f"DEBUG: Path CLEAR")
        return False