# main.py

import pathlib

import pygame
from implementation.game_builder import GameBuilder
from implementation.game import Game
# --- ייבוא המאזינים וה-EventManager וה-EventType ---
from implementation.publish_subscribe.event_manager import EventType
from implementation.publish_subscribe.move_logger_display import MoveLoggerDisplay
from implementation.publish_subscribe.subscribers import SoundSubscriber # וודא שהנתיב נכון

def main():
    """
    Main entry point for the game application.
    """
    # 1. הגדרת נתיבים ופרמטרים

    pygame.init()  # אתחול של pygame
    infoObject = pygame.display.Info()
    FULL_SCREEN_WIDTH = infoObject.current_w
    FULL_SCREEN_HEIGHT = infoObject.current_h
    ROOT_FOLDER = pathlib.Path(__file__).parent / "assets"
    BOARD_LAYOUT_FILE = "board.csv"
    BOARD_IMAGE_FILE = "board.png"  # שם הקובץ של תמונת הלוח
    BACKGROUND_IMAGE_FILE = "background.jpg"
    # מימדי הלוח והתאים
    BOARD_WIDTH = 8
    BOARD_HEIGHT = 8
    CELL_WIDTH_PIX = 85
    CELL_HEIGHT_PIX = 85

    try:
        # 2. בניית המשחק
        game_builder = GameBuilder(
            root_folder=ROOT_FOLDER,
            board_width=BOARD_WIDTH,
            board_height=BOARD_HEIGHT,
            cell_width_pix=CELL_WIDTH_PIX,
            cell_height_pix=CELL_HEIGHT_PIX,
            board_image_file=BOARD_IMAGE_FILE,
            background_image_file=BACKGROUND_IMAGE_FILE,
            screen_width=FULL_SCREEN_WIDTH, 
            screen_height=FULL_SCREEN_HEIGHT,

        )
        game: Game = game_builder.build_game(board_file=BOARD_LAYOUT_FILE)
        
        # --- *** זהו החלק החשוב שצריך להוסיף! *** ---
        # גישה ל-event_manager שנוצר בתוך ה-GameBuilder
        event_manager = game_builder.event_manager 

        # 1. יצירת מופעים של המאזינים
        sound_subscriber = SoundSubscriber() # יצרנו אותו

        # 2. רישום ה-SoundSubscriber באופן מפורש
        # MoveLoggerDisplay נרשם כבר ב-__init__ שלו כשיוצרים אותו.
        # SoundSubscriber צריך להירשם כאן, אלא אם כן שינית את ה-__init__ שלו כדי שירשם אוטומטית.
        event_manager.subscribe(EventType.PIECE_MOVED, sound_subscriber.on_piece_moved_sound)
        event_manager.subscribe(EventType.PIECE_CAPTURED, sound_subscriber.on_piece_captured_sound)
        event_manager.subscribe(EventType.PIECE_JUMPED, sound_subscriber.on_piece_jumped_sound)
        # --- *** סוף החלק החשוב שצריך להוסיף! *** ---

        # 3. הפעלת לולאת המשחק הראשית
        game.run()

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. Please check your asset paths.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during game setup or execution.")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()