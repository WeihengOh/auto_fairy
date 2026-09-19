import cv2  # https://docs.opencv.org/4.x/
import numpy as np
import pyautogui
import mss  # https://python-mss.readthedocs.io/index.html
from time import sleep
import os
import random

pyautogui.FAILSAFE = False

sct = mss.MSS()
default_monitor = sct.monitors[
    1
]  # https://python-mss.readthedocs.io/api.html#mss.tools.mss.base.MSSBase.monitors


def click_template_image(
    template_image_path: str,
    monitor=default_monitor,
    threshold: float = 0.7,
    number_of_clicks: int = 1,
):
    print(f"{template_image_path} search")
    template_image = cv2.imread(template_image_path, 1)

    # Screenshot
    # game_screenshot_path = "sct_{width}x{height}.png".format(**monitor)
    # sct_img = sct.grab((0, 0, monitor["width"], monitor["height"]))
    # mss.tools.to_png(sct_img.rgb, sct_img.size, output=game_screenshot_path)  # type:ignore
    # game_screenshot = cv2.imread(game_screenshot_path, 1)
    game_screenshot = np.array(sct.grab((0, 0, monitor["width"], monitor["height"])))
    game_screenshot = game_screenshot[:, :, :3]  # remove alpha

    # https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
    search_result = cv2.matchTemplate(
        game_screenshot, template_image, cv2.TM_CCOEFF_NORMED
    )

    # View Result
    # cv2.imshow('Result', result)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # Get Max Result
    # print(cv2.minMaxLoc(result))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(search_result)
    print(max_val)

    # print(np.where(result >= threshold))
    y_coords, x_coords = np.where(search_result >= threshold)  # type:ignore
    # the screenshot might have a different resolution/dimensions form the actual screen. 
    # the width & height reset multipliers are used to reset the w & h (screenshot's dimensions) to the actual screen's dimensions 
    width_reset_multiplier = game_screenshot.shape[1] / monitor["width"]
    height_reset_multiplier = game_screenshot.shape[0] / monitor["height"]
    w = template_image.shape[1]
    h = template_image.shape[0]
    if "fairy" in template_image_path:
        h = h*1.5

    if len(x_coords) > 0:

        # get monitor coordinates of the first match
        x, y = x_coords[0], y_coords[0]

        x /= width_reset_multiplier
        y /= height_reset_multiplier

        x_c = int((x + x + w) // 2)
        y_c = int((y + y + h) // 2)

        if number_of_clicks == 0:
            pyautogui.moveTo(x=x_c, y=y_c)
        else:
            for i in range(number_of_clicks):                 
                pyautogui.click(x=x_c, y=y_c)  # type:ignore
        return True 
    return False

to_click = []
filler_clicks = []
# for img in ./images add image name to to_click and filler_click
for file in os.listdir("images/main"):
    filename = os.fsdecode(file)
    to_click.append(filename)
for file in os.listdir("images/filler"):
    filename = os.fsdecode(file)
    filler_clicks.append(filename)
# place 'manual.png' at the front of the list (so presses manual before fairy in combat)
to_click.remove('manual.png')
to_click.insert(0, 'manual.png')

# loop through images to click until true, then move mouse to a filler image and wait 10 seconds
while True:
    for image in to_click:
        if click_template_image("images/main/" + image) is True:
            sleep(6)
            for filler in filler_clicks:
                click_template_image("images/filler/" + filler, number_of_clicks=0)
            break
    # change the order of images to click so we don't get stuck on one spot, but keep manual.png at the front
    copy = to_click[1:]
    random.shuffle(copy)
    to_click[1:] = copy
    sleep(10)
