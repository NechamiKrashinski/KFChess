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

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.board = board
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.user_input_queue: queue.Queue = queue.Queue()
        self.start_time_ns = time.time_ns()
        self.running = True

        # --- מצב בחירת עכבר ---
        self.selected_piece_id: Optional[str] = None
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.mouse_player_color: str = 'W' # צבע השחקן שמשחק עם העכבר

        # --- מצב בחירת מקלדת ---
        self.keyboard_cursor_cell: Tuple[int, int] = (0, 0)
        self.keyboard_selected_piece_id: Optional[str] = None
        self.keyboard_cursor_color: Tuple[int, int, int] = (0, 255, 255) # צהוב
        self.keyboard_cursor_thickness: int = 2
        self.keyboard_player_color: str = 'B' # צבע השחקן שמשחק עם המקלדת


    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return (time.time_ns() - self.start_time_ns) // 1_000_000

    def clone_board(self) -> Board:
        """Return a **brand-new** Board wrapping a copy of the background pixels."""
        return Board(
            cell_H_pix=self.board.cell_H_pix,
            cell_W_pix=self.board.cell_W_pix,
            cell_H_m=self.board.cell_H_m,
            cell_W_m=self.board.cell_W_m,
            W_cells=self.board.W_cells,
            H_cells=self.board.H_cells,
            img=self.board.img.copy()
        )

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling. (No changes needed here for keyboard,
           as keyboard events are handled in the main loop's cv2.waitKey)"""
        thread = threading.Thread(target=self._mouse_handler_loop, daemon=True)
        thread.start()

    def _mouse_handler_loop(self):
        """Handle mouse clicks and queue commands in a separate thread."""
        while self.running:
            time.sleep(0.01)

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

        while self.running:
            now = self.game_time_ms()

            for p in self.pieces.values():
                p.update(now)

            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd, now)

            self._draw(now)
            # _show() מטפל כעת גם בקלט מקלדת
            if not self._show():
                self.running = False

            if self._is_win():
                break

        self._announce_win()
        cv2.destroyAllWindows()

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
            if clicked_piece_id:
                # --- בדיקה חדשה: וודא שהכלי שייך לשחקן העכבר ---
                if clicked_piece_id[1] == self.mouse_player_color: # נניח שהתו השני ב-ID הוא הצבע
                    self.selected_piece_id = clicked_piece_id
                    self.selected_cell = clicked_cell
                    print(f"Mouse selected piece {clicked_piece_id} at {clicked_cell}")
                else:
                    print(f"Mouse cannot select opponent's piece: {clicked_piece_id}")
            else:
                print(f"No piece at {clicked_cell} for mouse selection.")
        else:
            target_cell = clicked_cell
            piece = self.pieces[self.selected_piece_id]
            moves = piece.get_moves(list(self.pieces.values()))

            if target_cell in moves:
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=self.selected_piece_id,
                    type="Move",
                    params=list(target_cell)
                )
                self.user_input_queue.put(cmd)
                print(f"Queued move command (Mouse): {self.selected_piece_id} → {target_cell}")
            else:
                print(f"Illegal move for {self.selected_piece_id} → {target_cell}")

            self.selected_piece_id = None
            self.selected_cell = None

    def _process_input(self, cmd: Command, now_ms: int):
        if cmd.piece_id not in self.pieces:
            return

        piece_moving = self.pieces[cmd.piece_id]

        if cmd.type == "Move":
            target_cell = tuple(cmd.params)

            piece_at_target_before_move = None
            for other_pid, other_piece in self.pieces.items():
                if other_pid != piece_moving.piece_id and \
                   other_piece.get_physics().get_cell() == target_cell:
                    piece_at_target_before_move = other_piece
                    break

            if piece_at_target_before_move:
                # לוודא שאי אפשר לאכול כלי של אותו צבע
                if piece_moving.piece_id[1] != piece_at_target_before_move.piece_id[1]:
                    print(f"Piece {piece_moving.piece_id} captured {piece_at_target_before_move.piece_id} at {target_cell}!")
                    del self.pieces[piece_at_target_before_move.piece_id]
                else:
                    print(f"ERROR: {piece_moving.piece_id} tried to move to {target_cell} which is occupied by friendly piece {piece_at_target_before_move.piece_id}. This indicates a bug in move validation.")
                    return # לא לבצע את המהלך

            piece_moving.on_command(cmd, now_ms)

        else:
            piece_moving.on_command(cmd, now_ms)

    def _draw(self, now_ms: int):
        """Draw the current game state, including the keyboard cursor."""
        cloned_board = self.clone_board()

        # ציור הכלים
        for p in self.pieces.values():
            p.draw_on_board(cloned_board, now_ms)

        # --- ציור סמן המקלדת ---
        cursor_col, cursor_row = self.keyboard_cursor_cell
        x_pix = cursor_col * self.board.cell_W_pix
        y_pix = cursor_row * self.board.cell_H_pix

        cloned_board.img.draw_rectangle(
            x_pix, y_pix,
            self.board.cell_W_pix, self.board.cell_H_pix,
            self.keyboard_cursor_color,
            self.keyboard_cursor_thickness
        )

        # אם כלי נבחר באמצעות המקלדת, נצייר סמן נוסף עליו
        if self.keyboard_selected_piece_id:
            selected_piece = self.pieces.get(self.keyboard_selected_piece_id)
            if selected_piece:
                sel_col, sel_row = selected_piece.get_physics().get_cell()
                sel_x_pix = sel_col * self.board.cell_W_pix
                sel_y_pix = sel_row * self.board.cell_H_pix
                cloned_board.img.draw_rectangle(
                    sel_x_pix, sel_y_pix,
                    self.board.cell_W_pix, self.board.cell_H_pix,
                    (0, 0, 255), # צבע אדום לבחירת כלי מקלדת
                    3 # עובי
                )

        self.current_frame = cloned_board.img.img

    def _show(self) -> bool:
        """Show the current frame and handle window events, including keyboard input."""
        cv2.imshow("Board", self.current_frame)
        key = cv2.waitKey(1) & 0xFF # קליטת מקש

        # --- טיפול בקלט מקלדת ---
        current_col, current_row = self.keyboard_cursor_cell
        moved = False

        if key == ord('w'):  # 'w'
            if current_row > 0:
                self.keyboard_cursor_cell = (current_col, current_row - 1)
                moved = True
        elif key == ord('s'): # 's'
            if current_row < self.board.H_cells - 1:
                self.keyboard_cursor_cell = (current_col, current_row + 1)
                moved = True
        elif key == ord('a'): # 'a'
            if current_col > 0:
                self.keyboard_cursor_cell = (current_col - 1, current_row)
                moved = True
        elif key == ord('d'): # 'd'
            if current_col < self.board.W_cells - 1:
                self.keyboard_cursor_cell = (current_col + 1, current_row)
                moved = True
        elif key == 13: # Enter key
            self._handle_keyboard_action(self.keyboard_cursor_cell)

        # השארת הדפסת קודי מקשים לבדיקה עתידית אם תרצה להוסיף תמיכה בחיצים שוב
        # if key != 255 and key != 27:
        #     print(f"Key pressed: {key}")

        if moved:
            print(f"Keyboard cursor moved to: {self.keyboard_cursor_cell}")


        if key == 27: # ESC key
            return False
        return True

    def _handle_keyboard_action(self, cell_coords: Tuple[int, int]):
        """Handles a keyboard action (like Enter press) at the current cursor cell."""
        clicked_piece_id = None
        for pid, piece in self.pieces.items():
            if piece.get_physics().get_cell() == cell_coords:
                clicked_piece_id = pid
                break

        if self.keyboard_selected_piece_id is None:
            # אם אין כלי נבחר, ננסה לבחור אחד בתא הנוכחי של הסמן
            if clicked_piece_id:
                # --- בדיקה חדשה: וודא שהכלי שייך לשחקן המקלדת ---
                if clicked_piece_id[1] == self.keyboard_player_color: # נניח שהתו השני ב-ID הוא הצבע
                    self.keyboard_selected_piece_id = clicked_piece_id
                    print(f"Keyboard selected piece {clicked_piece_id} at {cell_coords}")
                else:
                    print(f"Keyboard cannot select opponent's piece: {clicked_piece_id}")
            else:
                print(f"No piece at {cell_coords} for keyboard selection.")
        else:
            # אם כלי כבר נבחר, ננסה להזיז אותו לתא הנוכחי של הסמן
            target_cell = cell_coords
            piece_to_move = self.pieces[self.keyboard_selected_piece_id]
            moves = piece_to_move.get_moves(list(self.pieces.values()))

            if target_cell in moves:
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=self.keyboard_selected_piece_id,
                    type="Move",
                    params=list(target_cell)
                )
                self.user_input_queue.put(cmd)
                print(f"Queued move command (Keyboard): {self.keyboard_selected_piece_id} → {target_cell}")
            else:
                print(f"Illegal move for {self.keyboard_selected_piece_id} → {target_cell} by keyboard.")

            # איפוס הבחירה לאחר ניסיון הזזה
            self.keyboard_selected_piece_id = None

    def _is_win(self) -> bool:
        """Check if the game has ended based on king capture."""
        kings_on_board = self._get_all_kings_on_board()

        if 'W' not in kings_on_board and 'B' in kings_on_board:
            return True
        elif 'B' not in kings_on_board and 'W' in kings_on_board:
            return True
        elif len(kings_on_board) == 0:
            print("Warning: No kings found on board. Game ends in draw or error state.")
            return True

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
            print("Game over! It's a draw or an undecided state (both kings still on board).")

    def _get_all_pieces_on_board(self) -> List['Piece']:
        """Return a list of all pieces currently on the board."""
        return list(self.pieces.values())

    def _get_all_kings_on_board(self) -> Dict[str, Piece]:
        """Return a dictionary of kings currently on the board, mapped by their color."""
        kings = {}
        for p in self.pieces.values():
            if p.piece_id[0].upper() == 'K': # מזהה מלך לפי האות הראשונה
                kings[p.piece_id[1].upper()] = p # מזהה צבע לפי האות השנייה
        return kings