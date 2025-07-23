# import pytest
# import numpy as np
# import pathlib
# from implementation.mock_img import MockImg

# # נתיבים פיקטיביים לקובצי בדיקה (לא באמת קיימים, רק לצורך סימולציה)
# TEMP_DIR = pathlib.Path("temp_test_images") # עדיין נשתמש בזה לסגנון, גם אם הקבצים לא נוצרים בפועל
# TEST_IMAGE_3_CHANNEL_PATH = TEMP_DIR / "test_image_3_channel.png"
# TEST_IMAGE_4_CHANNEL_PATH = TEMP_DIR / "test_image_4_channel.png"
# TEST_IMAGE_GRAY_PATH = TEMP_DIR / "test_image_gray.png"
# NON_EXISTENT_PATH = TEMP_DIR / "non_existent.png"
# INVALID_IMAGE_PATH = TEMP_DIR / "invalid_image.txt" 
# LARGE_TEST_IMAGE_PATH = TEMP_DIR / "large_test_image.png"

# # Fixture לניקוי ה-Mock.traj ו-Mock.txt_traj לפני כל בדיקה
# @pytest.fixture(autouse=True)
# def reset_mock_img_data():
#     """מאתחל את נתוני התיעוד ב-MockImg לפני כל בדיקה."""
#     MockImg.reset()
#     yield


# # --- בדיקות למתודת read ---

# def test_read_sanity_sets_default_image_shape():
#     """
#     Arrange: יצירת אובייקט MockImg.
#     Act: קריאת תמונה (פיקטיבית).
#     Assert: ודא שהתמונה הפנימית של ה-mock אינה None ובעלת צורה צפויה (ברירת מחדל או שונתה).
#     """
#     # Arrange
#     img_obj = MockImg()

#     # Act
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # הנתיב לא משנה, רק מפעיל את הפונקציה

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (50, 50, 4) # גודל ברירת המחדל שהוגדר ב-mock


# def test_read_with_target_size_sets_correct_shape():
#     """
#     Arrange: יצירת אובייקט MockImg וגודל יעד.
#     Act: קריאת תמונה (פיקטיבית) עם גודל יעד.
#     Assert: ודא שהתמונה הפנימית של ה-mock בגודל היעד.
#     """
#     # Arrange
#     img_obj = MockImg()
#     target_size = (100, 150) # width, height

#     # Act
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH, target_size=target_size)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (target_size[1], target_size[0], 4) # (height, width, channels)


# def test_read_non_existent_file_raises_filenotfounderror():
#     """
#     Arrange: יצירת אובייקט MockImg ונתיב לקובץ שאינו קיים (לצורך סימולציה).
#     Act: ניסיון לקרוא את הקובץ.
#     Assert: ודא ש-FileNotFoundError נזרק על ידי ה-mock.
#     """
#     # Arrange
#     img_obj = MockImg()

#     # Act & Assert
#     with pytest.raises(FileNotFoundError):
#         img_obj.read(NON_EXISTENT_PATH)


# def test_read_invalid_image_file_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט MockImg ונתיב לקובץ לא תקין (לצורך סימולציה).
#     Act: ניסיון לקרוא את הקובץ.
#     Assert: ודא ש-ValueError נזרק על ידי ה-mock.
#     """
#     # Arrange
#     img_obj = MockImg()

#     # Act & Assert
#     with pytest.raises(ValueError, match="Mock: Could not read image from"):
#         img_obj.read(INVALID_IMAGE_PATH)


# # --- בדיקות למתודת clone ---

# def test_clone_sanity_check_returns_new_mock_instance():
#     """
#     Arrange: יצירת אובייקט MockImg.
#     Act: שיבוט שלו.
#     Assert: ודא שמוחזר אובייקט MockImg חדש ושונה מהמקור, עם תמונה בגודל זהה.
#     """
#     # Arrange
#     original_img_obj = MockImg()
#     original_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH, target_size=(70, 80)) # הגדר גודל ספציפי

#     # Act
#     cloned_img_obj = original_img_obj.clone()

#     # Assert
#     assert isinstance(cloned_img_obj, MockImg)
#     assert cloned_img_obj is not original_img_obj # ודא שזה אובייקט שונה
#     assert cloned_img_obj.img is not None
#     assert cloned_img_obj.img.shape == original_img_obj.img.shape # ודא שגודל התמונה זהה


# def test_clone_empty_mock_image_object():
#     """
#     Arrange: יצירת אובייקט MockImg ריק.
#     Act: שיבוט האובייקט הריק.
#     Assert: ודא שהאובייקט המשובט גם הוא ריק (img is None, או במקרה של mock, עם גודל ברירת המחדל).
#     """
#     # Arrange
#     original_img_obj = MockImg()
#     original_img_obj.img = None # הדמיית מצב שבו לא נטענה תמונה

#     # Act
#     cloned_img_obj = original_img_obj.clone()

#     # Assert
#     assert isinstance(cloned_img_obj, MockImg)
#     # כאשר img היה None, ה-mock clone יוצר תמונה בגודל ברירת מחדל (10x10)
#     assert cloned_img_obj.img is not None
#     assert cloned_img_obj.img.shape == (10, 10, 4)


# # --- בדיקות למתודת draw_on ---

# def test_draw_on_records_coordinates():
#     """
#     Arrange: יצירת שני אובייקטי MockImg.
#     Act: קריאה ל-draw_on עם קואורדינטות ספציפיות.
#     Assert: ודא שהקואורדינטות נרשמו ב-MockImg.traj.
#     """
#     # Arrange
#     target_img_obj = MockImg()
#     source_img_obj = MockImg()
#     x, y = 50, 60

#     # Act
#     source_img_obj.draw_on(target_img_obj, x, y)

#     # Assert
#     assert MockImg.traj == [(x, y)]


# def test_draw_on_multiple_calls_records_all_coordinates():
#     """
#     Arrange: יצירת אובייקטי MockImg.
#     Act: קריאה מרובה ל-draw_on.
#     Assert: ודא שכל הקואורדינטות נרשמו בסדר הנכון.
#     """
#     # Arrange
#     target_img_obj1 = MockImg()
#     source_img_obj1 = MockImg()
#     target_img_obj2 = MockImg()
#     source_img_obj2 = MockImg()

#     # Act
#     source_img_obj1.draw_on(target_img_obj1, 10, 20)
#     source_img_obj2.draw_on(target_img_obj2, 30, 40)

#     # Assert
#     assert MockImg.traj == [(10, 20), (30, 40)]


# def test_draw_on_source_img_none_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט MockImg ריק (מקור) ואובייקט MockImg טעון (יעד).
#     Act: ניסיון ציור.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     source_img_obj = MockImg()
#     source_img_obj.img = None # מדמה מצב של תמונה לא טעונה
#     target_img_obj = MockImg()

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot draw: current image is not loaded."):
#         source_img_obj.draw_on(target_img_obj, 0, 0)


# def test_draw_on_target_img_none_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט MockImg טעון (מקור) ואובייקט MockImg ריק (יעד).
#     Act: ניסיון ציור.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     source_img_obj = MockImg()
#     target_img_obj = MockImg()
#     target_img_obj.img = None # מדמה מצב של תמונת יעד לא טעונה

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot draw on: target image is not loaded."):
#         source_img_obj.draw_on(target_img_obj, 0, 0)


# def test_draw_on_alpha_out_of_range_raises_valueerror():
#     """
#     Arrange: יצירת אובייקטי MockImg, וערכי אלפא מחוץ לטווח.
#     Act: ניסיון ציור עם ערכי אלפא לא חוקיים.
#     Assert: ודא ש-ValueError נזרק עבור כל מקרה.
#     """
#     # Arrange
#     source_img_obj = MockImg()
#     target_img_obj = MockImg()

#     # Act & Assert - alpha < 0
#     with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0."):
#         source_img_obj.draw_on(target_img_obj, 0, 0, alpha=-0.1)

#     # Act & Assert - alpha > 1
#     with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0."):
#         source_img_obj.draw_on(target_img_obj, 0, 0, alpha=1.1)


# # --- בדיקות למתודת put_text (אם רלוונטי לממשק Img המקורי) ---

# def test_put_text_records_text_and_coordinates():
#     """
#     Arrange: יצירת אובייקט MockImg.
#     Act: קריאה ל-put_text עם טקסט וקואורדינטות.
#     Assert: ודא שהנתונים נרשמו ב-MockImg.txt_traj.
#     """
#     # Arrange
#     img_obj = MockImg()
#     test_text = "Hello World"
#     x, y = 10, 20

#     # Act
#     img_obj.put_text(test_text, x, y, 1.0) # font_size is required by mock signature

#     # Assert
#     assert MockImg.txt_traj == [((x, y), test_text)]


# def test_put_text_multiple_calls_records_all_data():
#     """
#     Arrange: יצירת אובייקט MockImg.
#     Act: קריאה מרובה ל-put_text.
#     Assert: ודא שכל הנתונים נרשמו בסדר הנכון.
#     """
#     # Arrange
#     img_obj = MockImg()

#     # Act
#     img_obj.put_text("First", 1, 1, 1.0)
#     img_obj.put_text("Second", 2, 2, 1.0)

#     # Assert
#     assert MockImg.txt_traj == [((1, 1), "First"), ((2, 2), "Second")]


# # --- בדיקות למתודת show ---

# def test_show_does_nothing():
#     """
#     Arrange: יצירת אובייקט MockImg.
#     Act: קריאה ל-show.
#     Assert: ודא שלא נזרקות שגיאות וששום דבר לא נרשם (אין ל-show תיעוד).
#     """
#     # Arrange
#     img_obj = MockImg()

#     # Act
#     img_obj.show() # אם לא נזרקה שגיאה, זה מספיק לבדיקה זו.

#     # Assert
#     # אין ל-show תיעוד ב-MockImg, אז אין מה לבדוק ב-traj/txt_traj
#     pass # הבדיקה עוברת אם לא נזרקה חריגה


# # --- בדיקות למתודת resize ---

# def test_resize_upscale_updates_shape():
#     """
#     Arrange: טעינת תמונה ב-MockImg.
#     Act: שינוי גודל להגדלה.
#     Assert: ודא שצורת התמונה הפנימית של ה-mock עודכנה לגודל החדש.
#     """
#     # Arrange
#     img_obj = MockImg()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # הגדר תמונה בגודל ברירת מחדל 50x50
#     new_width, new_height = 100, 100

#     # Act
#     img_obj.resize(new_width, new_height)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (new_height, new_width, 4)


# def test_resize_downscale_updates_shape():
#     """
#     Arrange: טעינת תמונה ב-MockImg.
#     Act: שינוי גודל להקטנה.
#     Assert: ודא שצורת התמונה הפנימית של ה-mock עודכנה לגודל החדש.
#     """
#     # Arrange
#     img_obj = MockImg()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # 50x50
#     new_width, new_height = 25, 25

#     # Act
#     img_obj.resize(new_width, new_height)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (new_height, new_width, 4)


# def test_resize_on_none_image_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט MockImg ריק.
#     Act: ניסיון לשינוי גודל.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = MockImg()
#     img_obj.img = None # מדמה מצב של תמונה לא טעונה

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot resize: no image has been loaded yet."):
#         img_obj.resize(10, 10)


# def test_resize_with_zero_width_raises_valueerror():
#     """
#     Arrange: טעינת תמונה ב-MockImg.
#     Act: ניסיון לשינוי גודל עם רוחב אפס.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = MockImg()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)

#     # Act & Assert
#     with pytest.raises(ValueError, match="New width and height must be positive."):
#         img_obj.resize(0, 10)


# def test_resize_with_negative_height_raises_valueerror():
#     """
#     Arrange: טעינת תמונה ב-MockImg.
#     Act: ניסיון לשינוי גודל עם גובה שלילי.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = MockImg()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)

#     # Act & Assert
#     with pytest.raises(ValueError, match="New width and height must be positive."):
#         img_obj.resize(10, -10)