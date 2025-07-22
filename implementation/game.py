import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from .board import Board
from .command import Command
from .piece import Piece
from .img import Img


class InvalidBoard(Exception):
    ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.board = board
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.user_input_queue: queue.Queue = queue.Queue()
        self.start_time_ns = time.time_ns()
        self.running = True
        self.selected_piece_id: Optional[str] = None
        self.selected_cell: Optional[Tuple[int, int]] = None



    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return (time.time_ns() - self.start_time_ns) // 1_000_000

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        # יוצר עותק עמוק של תמונת הלוח כדי למנוע ציור על הרקע המקורי
        return Board(
            cell_H_pix=self.board.cell_H_pix,
            cell_W_pix=self.board.cell_W_pix,
            cell_H_m=self.board.cell_H_m,
            cell_W_m=self.board.cell_W_m,
            W_cells=self.board.W_cells,
            H_cells=self.board.H_cells,
            img=self.board.img.clone()  # העתקה עמוקה כמו במחלקת Board.clone()
        )

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        thread = threading.Thread(target=self._mouse_handler_loop, daemon=True)
        thread.start()

    def _mouse_handler_loop(self):
        """Handle mouse clicks and queue commands in a separate thread."""
        while self.running:
            # Placeholder for mouse handling logic.
            # In a real game, this would listen for mouse events and create commands.
            # For now, we'll just simulate a command or sleep to prevent high CPU usage.
            time.sleep(0.01)

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        cv2.imshow("Board", self.board.img.img)
        cv2.setMouseCallback("Board", self._mouse_callback)

        # QWe2e5
        # The provided skeleton has a command queue, so let's start the thread.
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
            # The provided skeleton has a command queue. Let's process it.
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd, now)

            # (3) draw current position
            self._draw(now)
            if not self._show():
                self.running = False  # Set running flag to False if user closes window
            
            # (4) detect captures
            self._resolve_collisions(now)
            
            if self._is_win():
                break

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _mouse_callback(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        # חשב את תא הלוח שנלחץ
        col = x // self.board.cell_W_pix
        row = y // self.board.cell_H_pix
        clicked_cell = (col, row)

        # בדיקה אם יש כלי בתא שנלחץ
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
            occupied = [p.get_physics().get_cell() for pid, p in self.pieces.items()
            if pid != self.selected_piece_id and p.piece_id[1] != self.pieces[self.selected_piece_id].piece_id[1]]
            moves = piece.get_moves(occupied)
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
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd, now_ms)

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

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self, now_ms: int):
        to_remove = set()
        
        # מילון לשמירת מיקום נוכחי של כל כלי על הלוח (תא)
        piece_locations: Dict[Tuple[int, int], Piece] = {}
        for p in self.pieces.values():
            current_cell = p.get_physics().get_cell()
            # אם יש כבר כלי בתא הזה, זהו מצב של התנגשות (או לכידה)
            if current_cell in piece_locations:
                p1 = piece_locations[current_cell]
                p2 = p

                # ודא שהם מצבעים שונים
                if p1.piece_id[1] != p2.piece_id[1]:
                    # לכידה: הכלי שתפס הוא זה שנמצא כרגע בתנועה (אם רלוונטי)
                    # או הכלי שנכנס לתא אחרון (במשחק אסינכרוני זה יותר מורכב)
                    # לצורך הפשטות, נבחר כלי אחד שיכול ללכוד
                    if p1.get_physics().can_capture() and p2.get_physics().can_be_captured():
                        print(f"Piece {p1.piece_id} captures {p2.piece_id}!")
                        to_remove.add(p2.piece_id)
                    elif p2.get_physics().can_capture() and p1.get_physics().can_be_captured():
                        print(f"Piece {p2.piece_id} captures {p1.piece_id}!")
                        to_remove.add(p1.piece_id)
                    # טיפול במצב שבו אף אחד לא יכול ללכוד או שניהם יכולים
                    # לדוגמה: שניהם יכולים ללכוד -> שניהם נעלמים או שהראשון מנצח
                    # כרגע נשמור על הלוגיקה הקיימת (הכלי הראשון שנמצא מנצח)
                else:
                    # כלים מאותו צבע באותו תא - בעיה לוגית, אולי לדחוף אחד החוצה
                    # או למנוע את המהלך מלכתחילה. כרגע זה פשוט אומר שאין לכידה.
                    pass
            else:
                piece_locations[current_cell] = p

        # בצע את הסרת הכלים רק לאחר שעברנו על כל הכלים כדי למנוע שינוי רשימה תוך כדי איטרציה
        for pid in to_remove:
            if pid in self.pieces:
                del self.pieces[pid]
                
                       
    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        if len(self.pieces) <= 1:
            return True
        return False

    def _announce_win(self):
        """Announce the winner."""
        if len(self.pieces) == 1:
            winner = list(self.pieces.values())[0]
            print(f"Game over! The winner is {winner.piece_id}")
        else:
            print("Game over! It's a draw.")