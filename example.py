import os
from pathlib import Path
import cv2
from dotenv import load_dotenv
from implementation.img import Img

def main():
    print("Current working directory is:", os.getcwd())

    # טען משתני סביבה מהקובץ .env
    env_path = Path("assets") / ".env"
    load_dotenv(dotenv_path=env_path)

    # קבל את הנתיבים מתוך .env
    board_path = os.getenv("BOARD_PATH")
    # logo_base = os.getenv("LOGO_IMAGE_PATH")

    # ודא שמשתנים קיימים
    if board_path is None:
        raise ValueError("Missing BOARD_PATH in .env")
    # if logo_base is None:
    #     raise ValueError("Missing LOGO_IMAGE_PATH in .env")

    # בנה נתיב יחסי ללוגו
    logo = "pieces_resources/QW/states/jump/sprites/2.png"
    
    print("Trying to load image from:", logo)
    print("Full path:", os.path.abspath(logo)) 

    # טען את לוח המשחק
    canvas = Img().read(board_path)

    # טען את ה־piece
    piece = Img().read(logo, size=(100, 100), keep_aspect=True)

    # כתוב טקסט באמצע הלוח
    h, w = canvas.img.shape[:2]
    canvas.put_text("Demo", h // 2, w // 2, 3.0,
                    color=(255, 0, 0, 255), thickness=5)

    # צייר את ה־piece על הלוח
    piece.draw_on(canvas, 50, 50)
    canvas.show()

if __name__ == "__main__":
    main()
