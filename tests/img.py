# import pytest
# import numpy as np
# import pathlib
# import cv2
# from implementation.mo import Img  # ודא שהקובץ img_class.py נמצא באותה תיקייה


# # נתיבים לקובצי בדיקה (יש לוודא שקיימים או ליצור אותם לפני ההרצה)
# TEMP_DIR = pathlib.Path("temp_test_images")
# TEST_IMAGE_3_CHANNEL_PATH = TEMP_DIR / "test_image_3_channel.png"
# TEST_IMAGE_4_CHANNEL_PATH = TEMP_DIR / "test_image_4_channel.png"
# TEST_IMAGE_GRAY_PATH = TEMP_DIR / "test_image_gray.png"
# NON_EXISTENT_PATH = TEMP_DIR / "non_existent.png"
# INVALID_IMAGE_PATH = TEMP_DIR / "invalid_image.txt" # קובץ טקסט ריק לדוגמה
# LARGE_TEST_IMAGE_PATH = TEMP_DIR / "large_test_image.png"


# # Fixture ליצירת קובצי תמונה זמניים לפני הרצת הבדיקות
# @pytest.fixture(scope="module", autouse=True)
# def setup_test_images():
#     """יוצר קובצי תמונה פיקטיביים לשימוש בבדיקות."""
#     TEMP_DIR.mkdir(exist_ok=True)

#     # תמונה 3 ערוצים (BGR)
#     img_3_channel = np.zeros((50, 50, 3), dtype=np.uint8)
#     cv2.rectangle(img_3_channel, (10, 10), (40, 40), (0, 0, 255), -1)  # מלבן אדום
#     cv2.imwrite(str(TEST_IMAGE_3_CHANNEL_PATH), img_3_channel)

#     # תמונה 4 ערוצים (BGRA) - עם אלפא
#     img_4_channel = np.zeros((50, 50, 4), dtype=np.uint8)
#     img_4_channel[..., 0:3] = [255, 0, 0]  # כחול
#     img_4_channel[10:40, 10:40, 3] = 128  # חצי שקיפות במרכז
#     cv2.imwrite(str(TEST_IMAGE_4_CHANNEL_PATH), img_4_channel)

#     # תמונה בגווני אפור (1 ערוץ)
#     img_gray = np.zeros((50, 50), dtype=np.uint8)
#     cv2.circle(img_gray, (25, 25), 15, 200, -1)  # עיגול אפור בהיר
#     cv2.imwrite(str(TEST_IMAGE_GRAY_PATH), img_gray)

#     # קובץ לא תקין (ריק)
#     with open(INVALID_IMAGE_PATH, "w") as f:
#         f.write("")

#     # תמונה גדולה יותר לבדיקות draw_on
#     large_image = np.zeros((100, 100, 4), dtype=np.uint8)
#     large_image[..., :] = [255, 255, 255, 255]  # תמונה לבנה אטומה
#     cv2.imwrite(str(LARGE_TEST_IMAGE_PATH), large_image)

#     yield

#     # ניקוי קובצי הבדיקה לאחר סיום כל הבדיקות
#     for f in TEMP_DIR.iterdir():
#         f.unlink()
#     TEMP_DIR.rmdir()


# # --- בדיקות למתודת read ---

# def test_read_existing_3_channel_image_sanity():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לתמונת 3 ערוצים קיימת.
#     Act: קריאת התמונה.
#     Assert: ודא שהתמונה נטענה, אינה None, בעלת מידות וערוצים נכונים (4 ערוצים לאחר המרה).
#     """
#     # Arrange
#     img_obj = Img()

#     # Act
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (50, 50, 4)  # ודא המרה ל-4 ערוצים


# def test_read_existing_4_channel_image_sanity():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לתמונת 4 ערוצים קיימת.
#     Act: קריאת התמונה.
#     Assert: ודא שהתמונה נטענה, אינה None, ובעלת מידות וערוצים נכונים (נשארת 4 ערוצים).
#     """
#     # Arrange
#     img_obj = Img()

#     # Act
#     img_obj.read(TEST_IMAGE_4_CHANNEL_PATH)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (50, 50, 4)


# def test_read_grayscale_image_converts_to_bgra():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לתמונת גווני אפור.
#     Act: קריאת התמונה.
#     Assert: ודא שהתמונה נטענה, אינה None, ובעלת 4 ערוצים לאחר המרה.
#     """
#     # Arrange
#     img_obj = Img()

#     # Act
#     img_obj.read(TEST_IMAGE_GRAY_PATH)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape == (50, 50, 4)


# def test_read_with_target_size():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לתמונה, עם גודל יעד.
#     Act: קריאת התמונה עם גודל היעד.
#     Assert: ודא שהתמונה נטענה ובגודל היעד.
#     """
#     # Arrange
#     img_obj = Img()
#     target_size = (100, 100)

#     # Act
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH, target_size=target_size)

#     # Assert
#     assert img_obj.img is not None
#     assert img_obj.img.shape[1] == target_size[0]  # רוחב
#     assert img_obj.img.shape[0] == target_size[1]  # גובה


# def test_read_non_existent_file_raises_filenotfounderror():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לקובץ שאינו קיים.
#     Act: ניסיון לקרוא את הקובץ.
#     Assert: ודא ש-FileNotFoundError נזרק.
#     """
#     # Arrange
#     img_obj = Img()

#     # Act & Assert
#     with pytest.raises(FileNotFoundError):
#         img_obj.read(NON_EXISTENT_PATH)


# def test_read_invalid_image_file_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט Img ונתיב לקובץ שאינו תמונה תקינה.
#     Act: ניסיון לקרוא את הקובץ.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = Img()

#     # Act & Assert
#     with pytest.raises(ValueError, match="Could not read image"):
#         img_obj.read(INVALID_IMAGE_PATH)


# # --- בדיקות למתודת clone ---

# def test_clone_sanity_check_deep_copy():
#     """
#     Arrange: יצירת אובייקט Img, טעינת תמונה, ושיבוט שלה.
#     Act: שינוי התמונה המקורית.
#     Assert: ודא שהתמונה המשובטת נשארה ללא שינוי, המצביע שונה.
#     """
#     # Arrange
#     original_img_obj = Img()
#     original_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)
#     cloned_img_obj = original_img_obj.clone()

#     # Act
#     # שנה פיקסל בתמונה המקורית
#     original_img_obj.img[0, 0] = [0, 0, 0, 0]

#     # Assert
#     assert cloned_img_obj.img is not None
#     assert not np.array_equal(original_img_obj.img, cloned_img_obj.img)  # ודא שהם שונים
#     assert id(original_img_obj.img) != id(cloned_img_obj.img)  # ודא מצביעים שונים


# def test_clone_empty_image_object():
#     """
#     Arrange: יצירת אובייקט Img ריק.
#     Act: שיבוט האובייקט הריק.
#     Assert: ודא שהאובייקט המשובט גם הוא ריק (img is None).
#     """
#     # Arrange
#     original_img_obj = Img()

#     # Act
#     cloned_img_obj = original_img_obj.clone()

#     # Assert
#     assert cloned_img_obj.img is None


# # --- בדיקות למתודת draw_on ---

# def test_draw_on_sanity_check_basic_drawing():
#     """
#     Arrange: טעינת תמונת יעד ותמונת מקור.
#     Act: ציור תמונת המקור על היעד במיקום ספציפי.
#     Assert: ודא שפיקסלים בתמונת היעד השתנו כצפוי באזור הציור.
#     """
#     # Arrange
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)  # תמונה לבנה 100x100

#     source_img_obj = Img()
#     source_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)  # תמונה 50x50 אדומה במרכז

#     x, y = 10, 10
#     expected_top_left_color_source = source_img_obj.img[0, 0]
#     expected_center_color_source = source_img_obj.img[25, 25] # צבע אדום עם אלפא 255

#     # Act
#     target_img_obj.draw_on(source_img_obj, x, y)

#     # Assert
#     # בדוק פיקסל באזור שהייתה אמורה להיות תמונה מקורית
#     assert np.array_equal(target_img_obj.img[y, x], expected_top_left_color_source)
#     assert np.array_equal(target_img_obj.img[y + 25, x + 25], expected_center_color_source)


# def test_draw_on_with_alpha_blending():
#     """
#     Arrange: טעינת תמונות וקביעת ערך אלפא.
#     Act: ציור תמונה עם אלפא.
#     Assert: ודא שצבעי הפיקסלים באזור החפיפה משולבים בהתאם לאלפא.
#     """
#     # Arrange
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)  # תמונה לבנה (255,255,255,255)

#     source_img_obj = Img()
#     # קובע תמונת מקור עם פיקסל מרכזי בצבע כחול (255,0,0,128)
#     source_img_obj.read(TEST_IMAGE_4_CHANNEL_PATH)

#     x, y = 10, 10
#     alpha = 0.5
#     # חישוב צבע צפוי עבור פיקסל כחול חצי שקוף על רקע לבן
#     # B = 255 * 0.5 + 255 * (1-0.5) = 127.5 + 127.5 = 255
#     # G = 0 * 0.5 + 255 * (1-0.5) = 0 + 127.5 = 127.5
#     # R = 0 * 0.5 + 255 * (1-0.5) = 0 + 127.5 = 127.5
#     # A = 255 * 0.5 + 255 * (1-0.5) = 255 (בגלל שגם המקור וגם היעד אטומים אחרי המיזוג)
#     # הערה: ערוץ האלפא של תמונת היעד יישאר 255 אם היא לבנה אטומה
#     expected_b = int(source_img_obj.img[25, 25, 0] * alpha + target_img_obj.img[y + 25, x + 25, 0] * (1 - alpha))
#     expected_g = int(source_img_obj.img[25, 25, 1] * alpha + target_img_obj.img[y + 25, x + 25, 1] * (1 - alpha))
#     expected_r = int(source_img_obj.img[25, 25, 2] * alpha + target_img_obj.img[y + 25, x + 25, 2] * (1 - alpha))
    
#     # בשל אופן המיזוג, האלפא של היעד נשאר 255 אם הוא היה אטום
#     expected_alpha_channel = 255 
    
#     expected_color = np.array([expected_b, expected_g, expected_r, expected_alpha_channel], dtype=np.uint8)

#     # Act
#     target_img_obj.draw_on(source_img_obj, x, y, alpha=alpha)

#     # Assert
#     # בדוק פיקסל באזור המרכז של תמונת המקור, היכן שהייתה שקיפות (במקור)
#     # בדיקת ערכים עם סבילות קטנה בגלל חישובי נקודה צפה
#     actual_color = target_img_obj.img[y + 25, x + 25]
#     assert np.allclose(actual_color[:3], expected_color[:3], atol=1) # השווה רק BGR
#     assert actual_color[3] == expected_color[3] # אלפא צריך להיות מדויק


# def test_draw_on_source_img_none_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט Img ריק (מקור) ואובייקט Img טעון (יעד).
#     Act: ניסיון ציור.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     source_img_obj = Img() # source_img_obj.img is None
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot draw: current image is not loaded."):
#         source_img_obj.draw_on(target_img_obj, 0, 0)


# def test_draw_on_target_img_none_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט Img טעון (מקור) ואובייקט Img ריק (יעד).
#     Act: ניסיון ציור.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     source_img_obj = Img()
#     source_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)
#     target_img_obj = Img() # target_img_obj.img is None

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot draw on: target image is not loaded."):
#         source_img_obj.draw_on(target_img_obj, 0, 0)


# def test_draw_on_alpha_out_of_range_raises_valueerror():
#     """
#     Arrange: טעינת תמונות, וערכי אלפא מחוץ לטווח.
#     Act: ניסיון ציור עם ערכי אלפא לא חוקיים.
#     Assert: ודא ש-ValueError נזרק עבור כל מקרה.
#     """
#     # Arrange
#     source_img_obj = Img()
#     source_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)

#     # Act & Assert - alpha < 0
#     with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0."):
#         source_img_obj.draw_on(target_img_obj, 0, 0, alpha=-0.1)

#     # Act & Assert - alpha > 1
#     with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0."):
#         source_img_obj.draw_on(target_img_obj, 0, 0, alpha=1.1)


# def test_draw_on_image_fully_outside_bounds_no_change():
#     """
#     Arrange: טעינת תמונות, מיקום ציור כך שתמונת המקור כולה מחוץ לתמונת היעד.
#     Act: ציור.
#     Assert: ודא שתמונת היעד נשארה ללא שינוי.
#     """
#     # Arrange
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)
#     original_target_img_data = target_img_obj.img.copy() # שמור עותק

#     source_img_obj = Img()
#     source_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # 50x50

#     # Act - ציור לגמרי מחוץ לגבולות
#     target_img_obj.draw_on(source_img_obj, 200, 200)

#     # Assert
#     assert np.array_equal(target_img_obj.img, original_target_img_data)


# def test_draw_on_image_partially_outside_bounds():
#     """
#     Arrange: טעינת תמונות, מיקום ציור כך שתמונת המקור חורגת חלקית מגבולות היעד.
#     Act: ציור.
#     Assert: ודא שהציור התבצע רק באזורים החופפים.
#     """
#     # Arrange
#     target_img_obj = Img()
#     target_img_obj.read(LARGE_TEST_IMAGE_PATH)  # 100x100
#     original_target_img_data = target_img_obj.img.copy()

#     source_img_obj = Img()
#     source_img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)  # 50x50

#     # Act - ציור כך שרק חלק מהתמונה הפנימית יצויר
#     x, y = -25, -25 # יצייר רק את הרביע הדרום-מזרחי של תמונת המקור
#     target_img_obj.draw_on(source_img_obj, x, y)

#     # Assert
#     # ודא שהפיקסל ב- (0,0) (שהוא פיקסל של היעד) השתנה
#     assert not np.array_equal(target_img_obj.img[0, 0], original_target_img_data[0, 0])
#     # ודא שהפיקסל מחוץ לאזור החפיפה (למשל, 70,70) נשאר לבן (מגבולות תמונת היעד המקורית)
#     assert np.array_equal(target_img_obj.img[70, 70], [255, 255, 255, 255])


# # --- בדיקות למתודת resize ---

# def test_resize_upscale_sanity():
#     """
#     Arrange: טעינת תמונה.
#     Act: שינוי גודל להגדלה.
#     Assert: ודא שהמידות השתנו לגודל החדש.
#     """
#     # Arrange
#     img_obj = Img()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # 50x50
#     new_width, new_height = 100, 100

#     # Act
#     img_obj.resize(new_width, new_height)

#     # Assert
#     assert img_obj.img.shape[1] == new_width
#     assert img_obj.img.shape[0] == new_height


# def test_resize_downscale_sanity():
#     """
#     Arrange: טעינת תמונה.
#     Act: שינוי גודל להקטנה.
#     Assert: ודא שהמידות השתנו לגודל החדש.
#     """
#     # Arrange
#     img_obj = Img()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # 50x50
#     new_width, new_height = 25, 25

#     # Act
#     img_obj.resize(new_width, new_height)

#     # Assert
#     assert img_obj.img.shape[1] == new_width
#     assert img_obj.img.shape[0] == new_height


# def test_resize_no_change_in_dimensions():
#     """
#     Arrange: טעינת תמונה.
#     Act: קריאה ל-resize עם המידות הנוכחיות.
#     Assert: ודא שהמידות נשארו זהות (ולא נזרקה שגיאה).
#     """
#     # Arrange
#     img_obj = Img()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH) # 50x50
#     original_width, original_height = img_obj.img.shape[1], img_obj.img.shape[0]

#     # Act
#     img_obj.resize(original_width, original_height)

#     # Assert
#     assert img_obj.img.shape[1] == original_width
#     assert img_obj.img.shape[0] == original_height


# def test_resize_on_none_image_raises_valueerror():
#     """
#     Arrange: יצירת אובייקט Img ריק.
#     Act: ניסיון לשינוי גודל.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = Img() # img_obj.img is None

#     # Act & Assert
#     with pytest.raises(ValueError, match="Cannot resize: no image has been loaded yet."):
#         img_obj.resize(10, 10)


# def test_resize_with_zero_width_raises_valueerror():
#     """
#     Arrange: טעינת תמונה.
#     Act: ניסיון לשינוי גודל עם רוחב אפס.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = Img()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)

#     # Act & Assert
#     with pytest.raises(ValueError, match="New width and height must be positive."):
#         img_obj.resize(0, 10)


# def test_resize_with_negative_height_raises_valueerror():
#     """
#     Arrange: טעינת תמונה.
#     Act: ניסיון לשינוי גודל עם גובה שלילי.
#     Assert: ודא ש-ValueError נזרק.
#     """
#     # Arrange
#     img_obj = Img()
#     img_obj.read(TEST_IMAGE_3_CHANNEL_PATH)

#     # Act & Assert
#     with pytest.raises(ValueError, match="New width and height must be positive."):
#         img_obj.resize(10, -10)