import cv2
import mss
import numpy as np
import pygetwindow as gw
import time
import pyautogui
import random
import pytesseract
import re

click_enabled = False

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def random_delay():
    delay = random.uniform(1, 2)
    time.sleep(delay)

def activate_and_resize_window():
    try:
        window = gw.getWindowsWithTitle('Hustle Castle')[0]
        window.activate()
        time.sleep(0.1)
        window.resizeTo(972, 612)
        window.moveTo(0, 0)
        return window
    except IndexError:
        print("Окно с названием 'Hustle Castle' не найдено.")
        return None

def capture_screen(window):
    with mss.mss() as sct:
        bbox = {'top': window.top, 'left': window.left, 'width': window.width, 'height': window.height}
        screenshot = np.array(sct.grab(bbox))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
#        cropped_screenshot = screenshot[31:-8, 8:-8]
    return screenshot

def find_and_process_matches(screenshot, template):
    template_image = cv2.imread(template, cv2.IMREAD_UNCHANGED)
    
    if template_image is None:
        print(f"Не удалось загрузить шаблон: {template}")
        return []

    mask = None
    if template_image.shape[2] == 4:
        b, g, r, a = cv2.split(template_image)
        template_image = cv2.merge((b, g, r))
        mask = a

    result = cv2.matchTemplate(screenshot, template_image, cv2.TM_CCOEFF_NORMED, mask=mask)
    threshold = 0.7
    locations = np.where(result >= threshold)

    rectangles = []
    for pt in zip(*locations[::-1]):
        rectangles.append([int(pt[0]), int(pt[1]), template_image.shape[1], template_image.shape[0]])

    return rectangles

def save_result_image(screenshot, rectangles):
    if len(rectangles) > 0:
        for rect in rectangles:
            x, y, w, h = rect
            cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)

def click_coordinates(coordinates, name):
    x, y, width, height = coordinates
    random_x = x + random.randint(0, width - 1)
    random_y = y + random.randint(0, height - 1)
    
    random_delay()
    pyautogui.click(random_x, random_y)
    print(f"Кликнули по {name}")

def click_on_first_match(rectangles, readable_name):
    if len(rectangles) > 0:
        first_match = rectangles[0]
        center_x = first_match[0] + first_match[2] // 2
        center_y = first_match[1] + first_match[3] // 2
        click_coordinates([center_x, center_y, 1, 1], readable_name)
        return True
    return False

def preprocess_image_for_ocr(screenshot, coordinates):
    x, y, w, h = coordinates
    roi = screenshot[y:y+h, x:x+w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
#    lower_gray_white = np.array([180, 180, 180], dtype=np.uint8)
#    upper_gray_white = np.array([255, 255, 255], dtype=np.uint8)
#    mask = cv2.inRange(roi, lower_gray_white, upper_gray_white)
#    binary_image = cv2.bitwise_and(roi, roi, mask=mask)
#    binary_image[mask > 0] = [255, 255, 255]
    custom_config = r'--oem 3 --psm 7 tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(binary_image, config=custom_config)
    text = re.sub(r'\s+', '', text)
    formatted_text = re.sub(r"(?<=\d)(?=(\d{3})+$)", " ", text)
    roi_output_file = "recognized_fragment.png"
    cv2.imwrite(roi_output_file, binary_image)
    print(f"Сохранен фрагмент: {roi_output_file}")
    return formatted_text.strip()

def coordinate_fragments(window):
    fragment_names = ["dc_Random_skirmish.png", "tes2.png", "tes3.png"]
    
    screenshot = capture_screen(window)
    
    all_rectangles = []
    for fragment in fragment_names:
        rectangles = find_and_process_matches(screenshot, fragment)
        if len(rectangles) > 0:
            rectangles, _ = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
            print(f"Найдены координаты фрагмента {fragment}:")
            for rect in rectangles:
                x, y, w, h = rect
                print(f"[{x}, {y}, {w}, {h}]")
            all_rectangles.extend(rectangles)
    
    save_result_image(screenshot, all_rectangles)
    cv2.imwrite("rez_coordinate.png", screenshot)
    print("Сохранено изображение: rez_coordinate.png")
    
    if len(all_rectangles) > 0:
         click_on_first_match(all_rectangles, "найденный фрагмент")

def draw_rectangle_and_recognize_text(window):
    time_coordinates = [825, 57, 31, 28]
    screenshot = capture_screen(window)
    save_result_image(screenshot, [time_coordinates])
    recognized_text = preprocess_image_for_ocr(screenshot, time_coordinates)
    print(f"Распознанный текст: {recognized_text}")

    output_file = "rez_11.png"
    cv2.imwrite(output_file, screenshot)
    print(f"Фрагмент с текстом: {output_file}")

def draw_rectangles_and_click(window):
    rectangles = [
        ([100, 100, 50, 30], "Прямоугольник 1"),
        ([200, 150, 60, 40], "Прямоугольник 2"),
        ([300, 200, 70, 50], "Прямоугольник 3")
    ]

    screenshot = capture_screen(window)
    save_result_image(screenshot, [rect[0] for rect in rectangles])
    cv2.imwrite("rez_22.png", screenshot)
    print("Сохранено изображение: rez_22.png")

    for rect, name in rectangles:
        click_on_first_match([rect], name)

if __name__ == "__main__":
    window = activate_and_resize_window()
    if window:
        coordinate_fragments(window)

        
