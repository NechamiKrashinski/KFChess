# main.py

import pathlib
from implementation.game_builder import GameBuilder
from implementation.game import Game

def main():
    
    """
    Main entry point for the game application.
    """
    # 1. הגדרת נתיבים ופרמטרים
    ROOT_FOLDER = pathlib.Path(__file__).parent / "assets"
    BOARD_LAYOUT_FILE = "board.csv"
    BOARD_IMAGE_FILE = "board.png"  # שם הקובץ של תמונת הלוח
    
    # מימדי הלוח והתאים
    BOARD_WIDTH = 8
    BOARD_HEIGHT = 8
    CELL_WIDTH_PIX = 100
    CELL_HEIGHT_PIX = 100

    try:
        # 2. בניית המשחק
        game_builder = GameBuilder(
            root_folder=ROOT_FOLDER,
            board_width=BOARD_WIDTH,
            board_height=BOARD_HEIGHT,
            cell_width_pix=CELL_WIDTH_PIX,
            cell_height_pix=CELL_HEIGHT_PIX,
            board_image_file=BOARD_IMAGE_FILE
        )
        game: Game = game_builder.build_game(board_file=BOARD_LAYOUT_FILE)
        
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