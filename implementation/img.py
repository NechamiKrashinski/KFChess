import cv2
import numpy as np
import pathlib
from typing import Optional, Tuple

class Img:
    def __init__(self):
        self.img: Optional[np.ndarray] = None

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        """
        Reads an image from a given path and optionally resizes it.
        Defaults to loading as BGR (3 channels) unless explicitly needing alpha.
        """
        if not path.exists():
            raise FileNotFoundError(f"Image file not found at {path}")
        
        # טען כתמונה עם 3 ערוצים (BGR) כברירת מחדל.
        # אם יש ערוץ אלפא בקובץ, הוא יתעלם ממנו.
        self.img = cv2.imread(str(path), cv2.IMREAD_COLOR) 
        
        if self.img is None:
            raise ValueError(f"Could not read image from {path}. Check file format or corruption.")

        # כעת התמונה היא בוודאות 3 ערוצים (BGR).
        # אין צורך בהמרות ל-BGRA כאן, אלא אם כן תבחר במפורש לעבוד עם אלפא עבור כל התמונות.
        # אם אתה רוצה שכל התמונות יהיו BGRA, שקול לטעון אותן כ-IMREAD_UNCHANGED 
        # ולבצע המרה ל-BGRA רק אם הן BGR.
        # אבל לרוב הציורים, BGR מספיק.

        # --- השורות הבאות יוסרו או יתוקנו ע"פ ההחלטה האם לעבוד עם אלפא או BGR ---
        # if self.img.shape[2] == 3:
        #     self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
        # elif self.img.shape[2] == 4:
        #     pass
        # else:
        #     raise ValueError(f"Unsupported image channel count: {self.img.shape[2]}")
        # ----------------------------------------------------------------------
        
        # וודא שהתמונה היא uint8
        if self.img.dtype != np.uint8:
            self.img = self.img.astype(np.uint8)

        # וודא שהתמונה רציפה
        if not self.img.flags['C_CONTIGUOUS']:
            self.img = np.ascontiguousarray(self.img)


        if target_size:
            self.resize(target_size[0], target_size[1])

        return self

    def copy(self) -> 'Img':
        """Creates a deep copy of the Img object."""
        new_img_obj = Img()
        if self.img is not None:
            new_img_obj.img = self.img.copy()
        return new_img_obj

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        """Draws this image onto another Img object at specified coordinates with alpha blending."""
        if self.img is None or other_img.img is None:
            return

        # וודא ששתי התמונות הן BGR (3 ערוצים)
        # אם אחת מהן נטענה בשחור-לבן, נמיר אותה ל-BGR לצורך פעולת ציור זו.
        # זה טיפול בטוח כדי למנוע שגיאות shape.
        if len(self.img.shape) == 2:
            self.img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        if len(other_img.img.shape) == 2:
            other_img.img = cv2.cvtColor(other_img.img, cv2.COLOR_GRAY2BGR)
            
        # וודא ששתי התמונות הן uint8
        if self.img.dtype != np.uint8:
            self.img = self.img.astype(np.uint8)
        if other_img.img.dtype != np.uint8:
            other_img.img = other_img.img.astype(np.uint8)
            
        # וודא ששתי התמונות רציפות
        if not self.img.flags['C_CONTIGUOUS']:
            self.img = np.ascontiguousarray(self.img)
        if not other_img.img.flags['C_CONTIGUOUS']:
            other_img.img = np.ascontiguousarray(other_img.img)


        h_src, w_src, _ = self.img.shape # כעת בטוח שזה 3 ערוצים
        h_dst, w_dst, _ = other_img.img.shape # כעת בטוח שזה 3 ערוצים

        x_dst_start = max(0, x)
        y_dst_start = max(0, y)
        x_dst_end = min(w_dst, x + w_src)
        y_dst_end = min(h_dst, y + h_src)

        x_src_start = x_dst_start - x
        y_src_start = y_dst_start - y
        x_src_end = x_src_start + (x_dst_end - x_dst_start)
        y_src_end = y_src_start + (y_dst_end - y_dst_start)

        if x_dst_start >= x_dst_end or y_dst_start >= y_dst_end:
            return

        # חשוב: אנחנו לא לוקחים ערוץ אלפא מהתמונה (כי הנחנו שהיא BGR)
        # במקום זאת, נשתמש בפרמטר 'alpha' הכללי.
        roi_dst = other_img.img[y_dst_start:y_dst_end, x_dst_start:x_dst_end]
        roi_src = self.img[y_src_start:y_src_end, x_src_start:x_src_end]

        # --- השינוי העיקרי כאן: טיפול באלפא ללא ערוץ רביעי ---
        # השתמש ב-cv2.addWeighted למיזוג אלפא פשוט בין שתי תמונות BGR.
        # זה הרבה יותר בטוח ויעיל למיזוג ב-OpenCV.
        # ה-alpha כאן הוא המשקל של התמונה הראשונה (roi_src), והשני (roi_dst) הוא 1.0 - alpha.
        # ה-gamma הוא 0.0, וזו פשוט תוספת בהירות, נשתמש ב-0.
        cv2.addWeighted(roi_src, alpha, roi_dst, 1.0 - alpha, 0.0, roi_dst)
    def resize(self, new_width: int, new_height: int):
        """Resizes the image to the specified new_width and new_height."""
        if self.img is None:
            raise ValueError("Cannot resize empty image. 'img' attribute is None.")

        current_height, current_width = self.img.shape[:2]
        if new_width == current_width and new_height == current_height:
            return

        interpolation = cv2.INTER_AREA if (new_width < current_width or new_height < current_height) else cv2.INTER_LINEAR
        self.img = cv2.resize(self.img, (new_width, new_height), interpolation=interpolation)

    def get_width(self) -> int:
        return self.img.shape[1] if self.img is not None else 0

    def get_height(self) -> int:
        return self.img.shape[0] if self.img is not None else 0

    def put_text(self, txt: str, x: int, y: int, font_size: float, *args, **kwargs):
        pass

    def show(self):
        pass

    # --- פונקציה חדשה לציור מלבן (חדש) ---
    def draw_rectangle(self, x1: int, y1: int, width: int, height: int, color: Tuple[int, int, int], thickness: int):
        if self.img is None:
            print("Warning: Cannot draw rectangle on an uninitialized Img object.")
            return

        # 1. וודא שסוג הנתונים הוא np.uint8 (הסטנדרט לפיקסלים)
        if self.img.dtype != np.uint8:
            self.img = self.img.astype(np.uint8)

        # 2. וודא שהמטריצה רציפה בזיכרון (מאוד חשוב ל-OpenCV)
        if not self.img.flags['C_CONTIGUOUS']:
            self.img = np.ascontiguousarray(self.img)

        # 3. טיפול בערוצים: אם התמונה אפורה, המר ל-BGR.
        # **כאן קטע הקוד של הטיפול ב-4 ערוצים צריך להיעלם,
        # מכיוון שהנחנו ב-read() שכל התמונות יהיו BGR (3 ערוצים).**
        if len(self.img.shape) == 2: # תמונה בשחור לבן/אפור
            self.img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        # elif len(self.img.shape) == 3 and self.img.shape[2] == 4: # **REMOVE THIS BLOCK**
        #    self.img = self.img[:, :, :3]

        x2, y2 = x1 + width, y1 + height
        cv2.rectangle(self.img, (x1, y1), (x2, y2), color, thickness)