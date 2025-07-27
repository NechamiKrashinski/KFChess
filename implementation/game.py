import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional

from implementation.publish_subscribe.event_manager import EventManager, EventType
from implementation.publish_subscribe.move_logger_display import MoveLoggerDisplay # וודא ש-EventType מיובא
from .board import Board
from .command import Command
from .piece import Piece
from .img import Img

class InvalidBoard(Exception):
    ...

class Game:
    def __init__(self, pieces: List[Piece], board: Board, event_manager: EventManager, background_img: Img,move_logger_display: MoveLoggerDisplay):
        """Initialize the game with pieces, board, and optional event bus."""
        self.board = board
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.user_input_queue: queue.Queue = queue.Queue()
        self.start_time_ns = time.time_ns()
        self.running = True
        self.background_img = background_img
        self.screen_width: int = 0 
        self.screen_height: int = 0
        # --- מצב בחירת עכבר ---
        self.selected_piece_id: Optional[str] = None
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.mouse_player_color: str = 'W' # צבע השחקן שמשחק עם העכבר

        # --- מצב בחירת מקלדת ---
        self.keyboard_cursor_cell: Tuple[int, int] = (0, 0)
        self.keyboard_selected_piece_id: Optional[str] = None
        self.keyboard_cursor_color: Tuple[int, int, int] = (255, 0, 0) 
        self.keyboard_cursor_thickness: int = 7
        self.keyboard_player_color: str = 'B' 

        # הקצאת event_manager כעתה תכונה של המחלקה
        self.event_manager = event_manager 
        self.move_logger_display = move_logger_display
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return (time.time_ns() - self.start_time_ns) // 1_000_000

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
        
        # --- פרסום אירוע התחלת משחק ---
        self.event_manager.publish(EventType.GAME_START)

        while self.running:
            now = self.game_time_ms()

            for p in self.pieces.values():
                p.update(now)

            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd, now)

            self._draw(now)
            if not self._show():
                self.running = False

            if self._is_win():
                break

        self._announce_win()
        cv2.destroyAllWindows()

    def _mouse_callback(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        board_width = self.board.W_cells * self.board.cell_W_pix
        board_height = self.board.H_cells * self.board.cell_H_pix
        board_x_on_screen = (self.screen_width - board_width) // 2
        board_y_on_screen = (self.screen_height - board_height) // 2
            # --- התיקון המרכזי: הפחת את היסט הלוח מקואורדינטות העכבר ---
        # x_relative_to_board = x - board_x_on_screen
        # y_relative_to_board = y - board_y_on_screen
        
        col = (x - board_x_on_screen) // self.board.cell_W_pix
        row = (y - board_y_on_screen) // self.board.cell_H_pix
        
        if not (0 <= col < self.board.W_cells and 0 <= row < self.board.H_cells):
            print(f"Mouse click outside board: ({x}, {y}). Adjusted to: ({col}, {row}) but out of bounds.")
            self.selected_piece_id = None # ביטול בחירה אם יצא מהלוח
            self.selected_cell = None
            return
        
        
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
                    # print(f"Mouse selected piece {clicked_piece_id} at {clicked_cell}")
                else:
                    print(f"Mouse cannot select opponent's piece: {clicked_piece_id}")
            else:
                print(f"No piece at {clicked_cell} for mouse selection.")
        else:
            target_cell = clicked_cell
            piece = self.pieces[self.selected_piece_id]
            moves = piece.get_moves(list(self.pieces.values()))
            if( target_cell == self.selected_cell ):
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=self.selected_piece_id,
                    type="Jump",
                    params=list(target_cell)
                )
                self.user_input_queue.put(cmd)
                print(f"Queued jump command (Mouse): {self.selected_piece_id} → {target_cell}")
            else:
                if target_cell in moves:
                    cmd = Command(
                        timestamp=self.game_time_ms(),
                        piece_id=self.selected_piece_id,
                        type="Move",
                        params=list(target_cell),
                        source_cell=self.selected_cell
                    )
                    self.user_input_queue.put(cmd)
                else:
                    print(f"Illegal move for {self.selected_piece_id} → {target_cell}")
            # print(f"Queued move command (Mouse): {self.selected_piece_id} → {target_cell}")

            self.selected_piece_id = None
            self.selected_cell = None

    def _process_input(self, cmd: Command, now_ms: int):
        if cmd.piece_id not in self.pieces:
            return

        piece_moving = self.pieces[cmd.piece_id]
        original_cell = piece_moving.get_physics().get_cell() # שמור את התא המקורי לפני המהלך

        # --- טיפול בפקודת "Move" ---
        if cmd.type == "Move":
            target_cell = tuple(cmd.params)

            # 1. בדיקת הכאת "קפיצה" (Jump Capture)
            # הכלי הנע נכנס למשבצת בה כלי יריב נמצא במצב "קופץ" וטורף אותו.
            capturing_piece = None
            for other_pid, other_piece in self.pieces.items():
                if other_pid != piece_moving.piece_id and \
                   other_piece.get_physics().get_cell() == target_cell and \
                   other_piece.is_jump and \
                   other_piece.piece_id[1] != piece_moving.piece_id[1]: # לוודא שזה כלי יריב
                    capturing_piece = other_piece
                    break

            if capturing_piece:
                print(f"Piece {piece_moving.piece_id} moved into {target_cell} and was captured by {capturing_piece.piece_id} (jump capture)!")
                
                # פרסום אירוע הכאה מסוג "Jump Capture"
                self.event_manager.publish(
                    EventType.PIECE_CAPTURED,
                    piece_color=capturing_piece.piece_id[1], # צבע הכלי שביצע את ההכאה (הקופץ)
                    piece_type=capturing_piece.piece_id[0], # סוג הכלי שביצע את ההכאה
                    from_coords=capturing_piece.get_physics().get_cell(), # מיקום הכלי הקופץ (לא זז, רק "טרף")
                    to_coords=target_cell, # המיקום בו הכלי הנאכל עמד
                    captured_piece_type=piece_moving.piece_id[0], # סוג הכלי הנאכל
                    captured_piece_color=piece_moving.piece_id[1] # צבע הכלי הנאכל
                )
                
                del self.pieces[piece_moving.piece_id] # הכלי הנע נאכל
                capturing_piece.is_jump = False # מאפסים את דגל ה-jump של הכלי שקפץ
                return # **חשוב**: אם הייתה הכאה, לא נמשיך לבצע את המהלך ולא נפרסם PIECE_MOVED

            # 2. בדיקת אכילה רגילה
            # אם יש כלי יריב פגיע ב-target_cell, הכלי הנע יאכל אותו.
            piece_at_target_before_move = None
            for other_pid, other_piece in self.pieces.items():
                if other_pid != piece_moving.piece_id and \
                   other_piece.get_physics().get_cell() == target_cell and \
                   other_piece.is_vulnerable():  # אם הכלי פגיע (לא במצב קפיצה)
                    piece_at_target_before_move = other_piece
                    break

            if piece_at_target_before_move:
                # וודא שאי אפשר לאכול כלי של אותו צבע
                if piece_moving.piece_id[1] != piece_at_target_before_move.piece_id[1]:
                    print(f"Piece {piece_moving.piece_id} captured {piece_at_target_before_move.piece_id} at {target_cell}!")
                    
                    # פרסום אירוע הכאה מסוג "Regular Capture"
                    self.event_manager.publish(
                        EventType.PIECE_CAPTURED,
                        piece_color=piece_moving.piece_id[1], # צבע הכלי שביצע את ההכאה
                        piece_type=piece_moving.piece_id[0], # סוג הכלי שביצע את ההכאה
                        from_coords=original_cell, # מיקום מוצא
                        to_coords=target_cell, # מיקום יעד (שם הוכה הכלי)
                        captured_piece_type=piece_at_target_before_move.piece_id[0], # סוג הכלי שהוכה
                        captured_piece_color=piece_at_target_before_move.piece_id[1] # צבע הכלי שהוכה
                    )
                    
                    del self.pieces[piece_at_target_before_move.piece_id] # הסרת הכלי שהוכה
                    piece_moving.on_command(cmd, now_ms) # הכלי המבצע את ההכאה עדיין זז ליעד
                    return # **חשוב**: אם הייתה הכאה, לא נמשיך לפרסם PIECE_MOVED
                else:
                    print(f"ERROR: {piece_moving.piece_id} tried to move to {target_cell} which is occupied by friendly piece {piece_at_target_before_move.piece_id}. This indicates a bug in move validation.")
                    return  # לא לבצע את המהלך אם זה כלי ידידותי

            # 3. אם הגענו לכאן, לא התרחשה הכאה (לא "jump capture" ולא "regular capture").
            # לכן, נבצע את המהלך ונפרסם אירוע "PIECE_MOVED".
            piece_moving.on_command(cmd, now_ms)
            self.event_manager.publish(
                EventType.PIECE_MOVED,
                piece_color=piece_moving.piece_id[1], # צבע הכלי
                piece_type=piece_moving.piece_id[0], # סוג הכלי
                from_coords=original_cell, # מיקום מקור
                to_coords=target_cell # מיקום יעד
            )

        # --- טיפול בפקודת "Jump" ---
        elif cmd.type == "Jump":
            # כאן, פעולת "Jump" רק מגדירה את הכלי כ"קופץ" (משנה את מצבו)
            target_cell = tuple(cmd.params) # זהו המיקום הנוכחי של הכלי, בו הוא "ממתין"
            
            # הגדרת דגל ה-is_jump ל-True
            piece_moving.is_jump = True
            print(f"Piece {piece_moving.piece_id} is now in 'jump' state at {target_cell}.")
            
            # קריאה ל-on_command אם יש צורך לעדכן מצב פנימי אחר של הכלי הקופץ (לדוגמה, להשפיע על המצב הפיזיקלי)
            piece_moving.on_command(cmd, now_ms)
            
            # פרסום אירוע לכניסה למצב קפיצה.
            # שימו לב: כאן השתמשתי ב-EventType.PIECE_JUMPED ולא ב-PIECE_JUMPED_STATE
            # כפי שהצעתי קודם, מכיוון שזה נראה סביר יותר לתאר את האירוע,
            # אך ודא שזה שם האירוע שהגדרת ב-EventType.
            self.event_manager.publish(
                EventType.PIECE_JUMPED, # וודא שזה תואם את ההגדרה ב-EventType
                piece_color=piece_moving.piece_id[1],
                piece_type=piece_moving.piece_id[0],
                cell_coords=target_cell # המיקום שבו הכלי נמצא ונכנס למצב קפיצה
            )

    def _draw(self, now_ms: int):
        """
        מצייר את מצב המשחק הנוכחי, כולל סמן המקלדת, יומן המהלכים והניקוד.
        המתודה מציירת כעת את הרקע, לאחר מכן את הלוח עם הכלים והסמנים מעליו,
        ולבסוף מפעילה את MoveLoggerDisplay לציור טקסטים.
        """
        # 1. מתחילים עם עותק של תמונת הרקע הכללית.
        final_display_img_obj = self.background_img.copy() 

        # 2. יוצרים עותק של הלוח. הלוח המשובט הזה יכיל את ציור הכלים והסמנים.
        cloned_board = self.board.clone()

        # 3. ציור הכלים על הלוח המשובט.
        for p in self.pieces.values():
            p.draw_on_board(cloned_board, now_ms)

        # 4. ציור סמן המקלדת על הלוח המשובט.
        cursor_col, cursor_row = self.keyboard_cursor_cell
        x_pix = cursor_col * self.board.cell_W_pix
        y_pix = cursor_row * self.board.cell_H_pix

        cloned_board.img.draw_rectangle( 
            x_pix, y_pix,
            self.board.cell_W_pix, self.board.cell_H_pix,
            self.keyboard_cursor_color,
            self.keyboard_cursor_thickness
        )

        # 5. ציור סמן הכלי הנבחר עם המקלדת על הלוח המשובט.
        if self.keyboard_selected_piece_id:
            selected_piece = self.pieces.get(self.keyboard_selected_piece_id)
            if selected_piece:
                sel_col, sel_row = selected_piece.get_physics().get_cell()
                sel_x_pix = sel_col * self.board.cell_W_pix
                sel_y_pix = sel_row * self.board.cell_H_pix
                cloned_board.img.draw_rectangle( 
                    sel_x_pix, sel_y_pix,
                    self.board.cell_W_pix, self.board.cell_H_pix,
                    (0, 0, 255), 
                    3
                )
        
        # 6. עכשיו, לאחר שכל הכלים והסמנים צויירו על cloned_board.img,
        # נדביק את ה-Img הזה על תמונת הרקע הסופית.
        board_width = cloned_board.img.get_width()
        board_height = cloned_board.img.get_height()
        board_x_on_screen = (self.screen_width - board_width) // 2
        board_y_on_screen = (self.screen_height - board_height) // 2
        
        # הדבקת הלוח (עם הכלים והסמנים שצויירו עליו) על תמונת הרקע.
        cloned_board.img.draw_on(final_display_img_obj, board_x_on_screen, board_y_on_screen)

        # --- הוספה חדשה: קריאה למתודת ה-draw של MoveLoggerDisplay ---
        # העברת התמונה שעליה מציירים (final_display_img_obj.img) ומימדי המסך והלוח
        self.move_logger_display.draw(
            display_img=final_display_img_obj.img,
            display_width=self.screen_width,
            display_height=self.screen_height,
            board_x_offset=board_x_on_screen,
            board_y_offset=board_y_on_screen,
            board_width=board_width,
            board_height=board_height
        )

        # 7. שומרים את התמונה המורכבת הסופית ב-self.current_frame.
        self.current_frame = final_display_img_obj.img

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
                    self.keyboard_selected_piece_original_cell = cell_coords
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
            
            if(target_cell == self.keyboard_selected_piece_original_cell):
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=self.keyboard_selected_piece_id,
                    type="Jump",
                    params=list(target_cell)
                )
                self.user_input_queue.put(cmd)
            else:
                if target_cell in moves:
                    cmd = Command(
                        timestamp=self.game_time_ms(),
                        piece_id=self.keyboard_selected_piece_id,
                        type="Move",
                        params=list(target_cell),
                        source_cell=self.keyboard_selected_piece_original_cell
                    )
                    self.user_input_queue.put(cmd)
                    print(f"Queued move command (Keyboard): {self.keyboard_selected_piece_id} → {target_cell}")
                else:
                    print(f"Illegal move for {self.keyboard_selected_piece_id} → {target_cell} by keyboard.")

            # איפוס הבחירה לאחר ניסיון הזזה
            self.keyboard_selected_piece_id = None
            self.keyboard_selected_piece_original_cell = None

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

        winner_color: Optional[str] = None
        if not white_king_exists and black_king_exists:
            winner_color = 'black'
            print("Game over! Black wins (White King captured)!")
        elif not black_king_exists and white_king_exists:
            winner_color = 'white'
            print("Game over! White wins (Black King captured)!")
        elif not white_king_exists and not black_king_exists:
            winner_color = 'draw' # או 'none'
            print("Game over! Both kings captured? It's a draw (or error).")
        else:
            winner_color = 'none' # או 'undecided'
            print("Game over! It's a draw or an undecided state (both kings still on board).")

        # --- פרסום אירוע סיום משחק ---
        if winner_color:
            self.event_manager.publish(EventType.GAME_END, winner=winner_color)

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