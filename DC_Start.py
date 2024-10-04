
import cv2
import mss
import numpy as np
import pygetwindow as gw
import time
import pyautogui
import random
import os

next_floor_counter = 0
journey_counter = 0
key_journeys = 4
food_journeys = True

def set_console_size():
    os.system('mode con: cols=50 lines=8')
    time.sleep(5)
set_console_size()

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
        cropped_screenshot = screenshot[31:-8, 8:-8]
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

#def save_result_image(screenshot, rectangles):
#    if len(rectangles) > 0:
#        for rect in rectangles:
#            x, y, w, h = rect
#            cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)

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

def dc_point_map(window):
    global next_floor_counter

    dc_map_names = {
        "dc_Dangerous_Game.png": ("Опасная игра", press_dangerous_game),
        "dc_Camp.png": ("Лагерь", press_camp),
        "dc_Altar_of_Blood.png": ("Алтарь крови", press_altar_of_blood),
        "dc_Ally_in_Reflection.png": ("Союзник в отражении", press_ally_in_reflection),
        "dc_Random_skirmish.png": ("Случайная стычка", dc_point_start),
        "dc_Arena_of_Torment.png": ("Арена мучений", dc_point_start),
        "dc_Minion.png": ("Прислужник", dc_point_start),
        "dc_Guardians_Iair.png": ("Логово стража", dc_point_start)
    }

    screenshot = capture_screen(window)
    fragment_found = False

    for fragment, (readable_name, action_function) in dc_map_names.items():
        rectangles = find_and_process_matches(screenshot, fragment)
        
        if len(rectangles) > 0:
            fragment_found = True
            print(f"Найдена локация: {readable_name}")
#            save_result_image(screenshot, rectangles)
#            cv2.imwrite("rez_map.png", screenshot)
            
            for rect in rectangles:
                rect[1] -= 20
            if click_on_first_match(rectangles, readable_name):

                action_function(window)

    if not fragment_found:
        next_floor_counter += 1
        if next_floor_counter in [1, 2]:
            click_coordinates([782, 450, 167, 61], "next_floor")
            print(f"Пройден Этаж: {next_floor_counter}")
            time.sleep(8)
            dc_point_map(window)
        elif next_floor_counter == 3:
            click_coordinates([782, 528, 167, 61], "end_journey")
            time.sleep(1)
            click_coordinates([529, 520, 151, 65], "dc_home")
            click_coordinates([529, 520, 151, 65], "dc_home")
            time.sleep(10)
            next_floor_counter = 0
            dc_start_journey(window)

def dc_point_start(window):
    click_coordinates([396, 281, 180, 32], "dc_bt_deploy_the_best")
    time.sleep(1)
    screenshot = capture_screen(window)
    rectangles = find_and_process_matches(screenshot, "no_warrior.png")
    rectangles = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)[0]
    count_no_warrior = len(rectangles)
    print(f"Отсуствие бойцов: {count_no_warrior}")

#    save_result_image(screenshot, rectangles)
#    cv2.imwrite("rez_no_war.png", screenshot)
#    print("Сохранено изображение: rez_no_war.png")

    if count_no_warrior == 0:
        click_coordinates([552, 493, 145, 66], "dc_bt_quick_attack")
        dc_point_finish(window)

    elif 1 <= count_no_warrior <= 3:
        click_coordinates([552, 493, 145, 66], "dc_bt_quick_attack")
        click_coordinates([338, 368, 128, 65], "dc_bt_no_warrior")
        dc_point_finish(window)

    elif count_no_warrior >= 4:
        click_coordinates([913, 435, 47, 85], "dc_bt_win_map")
        click_coordinates([782, 528, 167, 61], "dc_bt_end_journey")
        click_coordinates([338, 368, 128, 65], "dc_bt_end_journey_yes")
        time.sleep(1)
        click_coordinates([529, 520, 151, 65], "dc_home")
        click_coordinates([529, 520, 151, 65], "dc_home")
        time.sleep(8)
        dc_start_journey(window)

def dc_point_finish(window):
    time.sleep(2)

    dc_point_names = {
        "dc_point_defeat.png": "Поражение",
        "dc_point_victory.png": "Победа"
    }

    victory_defeat_fragments = list(dc_point_names.keys())
    
    screenshot = capture_screen(window)
    
    found_victory = False

    for fragment in victory_defeat_fragments:
        rectangles = find_and_process_matches(screenshot, fragment)
        if len(rectangles) > 0:
            print(f"Статус боя: {dc_point_names[fragment]}")
            if fragment == "dc_point_victory.png":
                found_victory = True
            break

    dc_bt_home = [415, 521, 142, 66]
    click_coordinates(dc_bt_home, "dc_bt_home")

    if found_victory:
        blessings_coordinates = {
            "selected blessing 1": ([146, 122, 186, 332]),
            "selected blessing 2": ([392, 122, 186, 322]),
            "selected blessing 3": ([642, 122, 186, 322])
        }

        random_blessing = random.choice(list(blessings_coordinates.items()))
        click_coordinates(random_blessing[1], random_blessing[0])

        dc_confirm_selection = [402, 507, 166, 65]
        click_coordinates(dc_confirm_selection, "dc_confirm_selection")
    time.sleep(3)
    dc_point_map(window)

def press_dangerous_game(window):
    dangerous_game_coordinates = {
        "dc_bt_move_on": [505, 138, 199, 133],
        "dc_bt_finish_selection": [710, 473, 174, 66]
    }
    for name, coords in dangerous_game_coordinates.items():
        click_coordinates(coords, name)
    time.sleep(1)
    dc_point_map(window)

def press_camp(window):
    screenshot = capture_screen(window)
    dead_warrior_rectangles = find_and_process_matches(screenshot, "dead_warrior.png")
    
    if len(dead_warrior_rectangles) > 0:
        print("Найден фрагмент dead_warrior.png.")
        click_coordinates([377, 141, 222, 140], "dc_bt_02")
    else:
        print("Фрагмент dead_warrior.png не найден.")
        click_coordinates([644, 141, 222, 140], "dc_bt_claim_reward")
    
    click_coordinates([710, 473, 174, 66], "dc_bt_finish_selection_1")
    click_coordinates([341, 371, 121, 62], "dc_bt_finish_selection_2")
    click_coordinates([408, 510, 155, 62], "dc_bt_closed")
    time.sleep(1)

    dc_point_map(window)

def press_altar_of_blood(window):
    altar_of_blood_coordinates = {
        "dc_bt_move_on": [660, 160, 199, 133],
        "dc_bt_finish_selection": [709, 497, 174, 66],
        "dc_bt_close": [407, 510, 156, 60]
    }
    for name, coords in altar_of_blood_coordinates.items():
        click_coordinates(coords, name)
    time.sleep(1)
    dc_point_map(window)

def press_ally_in_reflection(window):
    ally_in_reflection_coordinates = {
        "dc_bt_put_squad": [710, 474, 173, 65],
        "dc_bt_close": [402, 507, 166, 65]
    }
    for name, coords in ally_in_reflection_coordinates.items():
        click_coordinates(coords, name)
    time.sleep(1)
    dc_point_map(window)

def dc_start_journey(window):
    global journey_counter
    global next_floor_counter
    global food_journeys

    if food_journeys:
        click_coordinates([153, 146, 181, 40], "dc_bt_food")
    
    if journey_counter < key_journeys:
        click_coordinates([262, 515, 135, 57], "Participate")
        click_coordinates([296, 289, 179, 35], "Deploy the best")
        click_coordinates([418, 511, 138, 54], "Confirm")
        click_coordinates([338, 368, 128, 65], "Attack!")
        time.sleep(8)

        journey_counter += 1
        print(f"Выполнено путешествий: {journey_counter}")

        dc_point_map(window)
    else:
        print("Достигнуто максимальное количество путешествий.")

if __name__ == "__main__":
    window = activate_and_resize_window()
    if window:
        dc_start_journey(window)
