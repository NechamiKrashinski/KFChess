import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from .board import Board
from .command import Command
from .piece import Piece # וודא ייבוא נכון
from .img import Img


class InvalidBoard(Exception):
    ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.board = board
        # 💡 תיקון: מחיקת שורת הכפילות. self.pieces מוגדר כבר כאן.
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces} 
        self.user_input_queue: queue.Queue = queue.Queue()
        self.start_time_ns = time.time_ns()
        self.running = True
        self.selected_piece_id: Optional[str] = None
        self.selected_cell: Optional[Tuple[int, int]] = None
        # self.pieces: Dict[str, Piece] = {} # ⚠️ שורה זו הייתה כפולה, נמחקה

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return (time.time_ns() - self.start_time_ns) // 1_000_000

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return Board(
            cell_H_pix=self.board.cell_H_pix,
            cell_W_pix=self.board.cell_W_pix,
            cell_H_m=self.board.cell_H_m,
            cell_W_m=self.board.cell_W_m,
            W_cells=self.board.W_cells,
            H_cells=self.board.H_cells,
            img=self.board.img.clone()
        )

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        thread = threading.Thread(target=self._mouse_handler_loop, daemon=True)
        thread.start()

    def _mouse_handler_loop(self):
        """Handle mouse clicks and queue commands in a separate thread."""
        while self.running:
            time.sleep(0.01)

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        cv2.imshow("Board", self.board.img.img)
        cv2.setMouseCallback("Board", self._mouse_callback)

        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            cmd = Command(
                timestamp=start_ms,
                piece_id=p.piece_id,
                type="init",
                params=p.get_physics().get_pos()
            )
            p.on_command(cmd, start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while self.running:
            now = self.game_time_ms()

            # (1) update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd, now) # כאן מתבצעת הלכידה

            # (3) draw current position
            self._draw(now)
            if not self._show():
                self.running = False

            # (4) detect captures - 💡 הסר את הקריאה למתודה הזו מכאן
            # self._resolve_collisions(now) 

            if self._is_win():
                break

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _mouse_callback(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        col = x // self.board.cell_W_pix
        row = y // self.board.cell_H_pix
        clicked_cell = (col, row)

        clicked_piece_id = None
        for pid, piece in self.pieces.items():
            if piece.get_physics().get_cell() == clicked_cell:
                clicked_piece_id = pid
                break

        if self.selected_piece_id is None:
            # קליק ראשון: בחרי כלי
            if clicked_piece_id:
                self.selected_piece_id = clicked_piece_id
                self.selected_cell = clicked_cell
                print(f"Selected piece {clicked_piece_id} at {clicked_cell}")
        else:
            # קליק שני: נסי להזיז ליעד
            target_cell = clicked_cell
            piece = self.pieces[self.selected_piece_id]

            # 💡 תיקון והתאמה: העברת רשימת כל הכלים ל-get_moves
            # Piece.get_moves תדאג לבנות את שתי הרשימות (all_occupied, occupied_enemy)
            # מתוך רשימת כל הכלים.
            moves = piece.get_moves(list(self.pieces.values()))
            
            if target_cell in moves:
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=self.selected_piece_id,
                    type="Move",
                    params=list(target_cell)
                )
                self.user_input_queue.put(cmd)
                print(f"Queued move command: {self.selected_piece_id} → {target_cell}")
            else:
                print(f"Illegal move for {self.selected_piece_id} → {target_cell}")

            # אפס בחירה תמיד אחרי קליק שני
            self.selected_piece_id = None
            self.selected_cell = None


    
    def _process_input(self, cmd: Command, now_ms: int):
        if cmd.piece_id not in self.pieces:
            # הכלי שאמור לזוז אינו קיים (ייתכן שנלכד בתור קודם)
            return

        piece_moving = self.pieces[cmd.piece_id]
        
        if cmd.type == "Move":
            target_cell = tuple(cmd.params) # התא אליו הכלי רוצה לזוז

            # לפני ביצוע הפקודה, וודא שהתא היעד ריק או מכיל אויב
            # הלוגיקה הזו כבר נעשית ב-piece.get_moves, אבל זוהי בדיקת בטיחות
            # והיא המקום הנכון לטפל בלכידה
            
            piece_at_target_before_move = None
            for other_pid, other_piece in self.pieces.items():
                # וודא שזה לא הכלי שזז ושהתא של הכלי האחר הוא תא היעד
                if other_pid != piece_moving.piece_id and \
                   other_piece.get_physics().get_cell() == target_cell:
                    piece_at_target_before_move = other_piece
                    break
            
            if piece_at_target_before_move:
                # אם יש כלי בתא היעד
                if piece_moving.piece_id[1] != piece_at_target_before_move.piece_id[1]:
                    # זה כלי אויב - לכידה!
                    print(f"Piece {piece_moving.piece_id} captured {piece_at_target_before_move.piece_id} at {target_cell}!")
                    del self.pieces[piece_at_target_before_move.piece_id]
                    # וודא שהכלי הנלכד באמת נמחק מהדיקשנרי.
                else:
                    # זה כלי ידידותי - זה לא אמור לקרות אם get_moves עובד נכון
                    print(f"ERROR: {piece_moving.piece_id} tried to move to {target_cell} which is occupied by friendly piece {piece_at_target_before_move.piece_id}. This indicates a bug in move validation.")
                    # במקרה כזה, אנו לא רוצים שהכלי יזוז.
                    return # חשוב: עצור את התנועה!

            # בצע את הפקודה - הכלי זז לתא החדש (אשר עכשיו או ריק או היה בו אויב ונמחק)
            piece_moving.on_command(cmd, now_ms)
            
        else:
            # אם זה לא פקודת "Move" (לדוגמה, "init")
            piece_moving.on_command(cmd, now_ms)


    def _draw(self, now_ms: int):
        """Draw the current game state."""
        cloned_board = self.clone_board()
        for p in self.pieces.values():
            p.draw_on_board(cloned_board, now_ms)
        self.current_frame = cloned_board.img.img

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        cv2.imshow("Board", self.current_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC key
            return False
        return True

  
    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended based on king capture."""
        kings_on_board = self._get_all_kings_on_board()
        
       
        # תנאי ניצחון: אם למשחק נשאר מלך אחד בלבד
        if 'W' not in kings_on_board and 'B' in kings_on_board:
            # המלך הלבן נאכל, שחור מנצח
            return True
        elif 'B' not in kings_on_board and 'W' in kings_on_board:
            # המלך השחור נאכל, לבן מנצח
            return True
        elif len(kings_on_board) == 0:
            # אם אין מלכים בכלל (מצב שגיאה או סיום לא סטנדרטי)
            print("Warning: No kings found on board. Game ends in draw or error state.")
            return True # נחשיב כסיום משחק (לרוב תיקו)
        
        # אם יש עדיין שני מלכים, המשחק לא הסתיים בגלל לכידת מלך
        return False

    def _announce_win(self):
        """Announce the winner based on remaining kings."""
        kings_on_board = self._get_all_kings_on_board()
        
        white_king_exists = 'W' in kings_on_board
        black_king_exists = 'B' in kings_on_board

        if not white_king_exists and black_king_exists:
            print("Game over! Black wins (White King captured)!")
        elif not black_king_exists and white_king_exists:
            print("Game over! White wins (Black King captured)!")
        elif not white_king_exists and not black_king_exists:
            print("Game over! Both kings captured? It's a draw (or error).")
        else:
            # במצב שחמט רגיל, זה יהיה מצב של תיקו (stalemate, insufficient material, etc.)
            # או שהמשחק פשוט עדיין לא הסתיים (כאשר שני מלכים עדיין קיימים).
            # בהתאם לחוקי התיקו המורכבים יותר שהזכרנו, זה יכול להיות גם תיקו.
            print("Game over! It's a draw or an undecided state (both kings still on board).")

# 💡 תיקון: פונקציות העזר האלה שייכות למחלקה Game, והיו מחוץ לה
    def _get_all_pieces_on_board(self) -> List['Piece']:
        """מחזירה רשימה של כל אובייקטי הכלים שנמצאים כרגע על הלוח."""
        return list(self.pieces.values())

    # ⚠️ הערה: פונקציה זו _handle_piece_selection לא נקראת ישירות מתוך run() או _mouse_callback
    # הלוגיקה שלה שולבה ישירות ב- _mouse_callback
    # אם היא מיועדת להיות קריאה חיצונית או חלק מממשק אחר, השאר אותה
    # אחרת, היא מיותרת כעת. אני אשאיר אותה כרגע אבל עם הערה.
    def _handle_piece_selection(self, selected_piece_id: str):
        # הלוגיקה של הפונקציה הזו ממומשת כעת בתוך _mouse_callback באופן ישיר.
        # אם יש לה מטרה נוספת, השאר אותה. אחרת, היא מיותרת.
        print(f"DEBUG: _handle_piece_selection called for {selected_piece_id}. This function's logic is typically handled by _mouse_callback now.")
        selected_piece = self.pieces.get(selected_piece_id)
        if selected_piece:
            possible_moves = selected_piece.get_moves(self._get_all_pieces_on_board())
            # ... השתמש ב-possible_moves כדי להציג את האפשרויות על הלוח.
            # זה כבר מטופל ב-_mouse_callback.

    def _get_all_kings_on_board(self) -> Dict[str, Piece]:
        """מחזירה מילון של מלכים שנמצאים כרגע על הלוח, ממופים לפי צבעם."""
        kings = {}
        for p in self.pieces.values():
            if p.piece_id[0].upper() == 'K': # 'K' מייצג מלך
                kings[p.piece_id[1].upper()] = p # שמור מלך לפי צבעו (W/B)
        return kings