from PIL import ImageGrab
import time
from typing import Optional
from ctypes import windll, create_unicode_buffer
import json
import subprocess
import os
from datetime import datetime
import keyboard  # You will have to install this lib
import sys
import win32con  # part of the pywin32 lib bundle (install with pip install pywin32)
import win32gui
import win32api
import threading


try:
    with open("highscores.json", "r") as f:
        high_scores = json.load(f)
except FileNotFoundError as e:
    with open("highscores.json", "w") as f:
        json.dump({}, f)
        high_scores = {}

click_delay = .005  # delay of auto-click-functionality
block_other_click_spam = True  # blocks the start of right click-spam if left click is already active and vice versa
block_keys = "wasdepuml1234567"  # keys that might block the combination of l + alt + print_screen
lock = True  # start of the lock (depending on your application, change this to True)
blacklist = {"diep", "youtube", "minecraft"}  # everything you want to block, add your own games here.
explicit_whitelist = {"pycharm",
                      "discord"}  # every thing you do not want to close, even though its title may contain game titles.


def error_handler(method):
    def tested(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as exception:
            print(exception)
    return tested


def get_foreground_window_title() -> Optional[str]:
    hwnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hwnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hwnd, buf, length + 1)

    return buf.value if buf.value else None


@error_handler
def take_pic():
    if "diep.io" in get_foreground_window_title():
        [keyboard.block_key(k) for k in block_keys]
        keyboard.press("l")
        time.sleep(.1)
        keyboard.press_and_release("alt+prtscn")
        time.sleep(.05)
        keyboard.release("l")
        [keyboard.unblock_key(k) for k in block_keys]
        time.sleep(.1)
        img = ImageGrab.grabclipboard()
        time.sleep(.1)
        img2 = img.crop((3 * img.width // 7, 13 * img.height // 14, 4 * img.width // 7, img.height))
        for x in range(img2.width):
            for y in range(img2.height):
                p = img2.getpixel((x, y))
                img2.putpixel((x, y), (0, 0, 0) if all(map(lambda c: c > 185, p)) and not all(
                    map(lambda c: 207 > c > 195, p)) and p not in [(198, 198, 198), (205, 205, 205),
                                                                   (202, 202, 202)] else (0xff, 0xff, 0xff))
        img2.save("testimg.png", "PNG")
        time.sleep(.1)
        prc = subprocess.run("Tesseract-OCR\\tesseract.exe testimg.png stdout", shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        text = prc.stdout.strip().split(b"\r\n")
        _score, _class = None, None
        for l in text:
            if b"Score" in l.strip():
                _score = int(l.strip().split()[1].decode().replace(",", "").replace(".", ""))
            elif l.strip().startswith(b"Lvl "):
                _class = l.strip().split()[2].decode()
        if _score is not None and _class is not None:
            print(_class, "with", _score)
            if _class in high_scores:
                if _score > high_scores[_class][0]:
                    if high_scores[_class][1] in os.listdir("highscores"):
                        os.remove("highscores\\" + high_scores[_class][1])
                else:
                    return
            filename = _class + "-" + str(_score) + "-" + datetime.now().strftime("%m~%d~%Y-%H~%M") + ".png"
            high_scores[_class] = (_score, filename)
            img.save("highscores\\" + filename, "PNG")
            with open("highscores.json", "w") as high_scores_json_file:
                json.dump(high_scores, high_scores_json_file)
        else:
            print(text)
            take_pic()  # Fixme: maybe not a good idea...
        # Imgur??? https://steemit.com/programming/@synapse/how-to-upload-images-to-imgur-using-python


def toggle_survival():
    global survival_activated
    if "diep.io" in get_foreground_window_title():
        survival_activated = not survival_activated
        print("survival mode", "activated" if survival_activated else "deactivated")


def minimize_blacklisted():
    if not lock:  # check the lock
        return
    hwnd = windll.user32.GetForegroundWindow()  # get foreground window
    length = windll.user32.GetWindowTextLengthW(hwnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hwnd, buf, length + 1)  # read the title
    if buf.value is not None and any(map(lambda x: x in buf.value.lower(), blacklist)) and not any(
            map(lambda x: x in buf.value.lower(),
                explicit_whitelist)):  # is any of the blacklisted items contained in the active windows title?
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)


def toggle_game_close():  # toggle the lock and give a message about the new status in the console.
    global lock
    lock = not lock
    print("Lock is now " + ("active" if lock else "inactive"))


def exit_script():  # give a message while exiting.
    print("exiting now...")
    sys.exit()


def left_click(x=None, y=None):
    if x is not None and y is not None:
        win32api.SetCursorPos((x, y))
    else:
        flags, cursor, (x, y) = win32gui.GetCursorInfo()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def right_click(x=None, y=None):
    if x is not None and y is not None:
        win32api.SetCursorPos((x, y))
    else:
        flags, cursor, (x, y) = win32gui.GetCursorInfo()
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)


@error_handler
def survive():
    n = 0
    while True:
        if survival_activated and "diep.io" in get_foreground_window_title():
            keyboard.press("a")
            time.sleep(2)
            keyboard.release("a")
            keyboard.press("d")
            time.sleep(2)
            keyboard.release("d")
            time.sleep(2)
            n += 1
            if n % 10 == 0:
                take_pic()
        time.sleep(10)


@error_handler
def auto_click_left():
    global left_click_lock_active, right_click_lock_active
    while True:
        while (not (win32api.GetKeyState(0x01) not in (1, 0, -1) and keyboard.is_pressed(
                'ctrl+shift'))) or right_click_lock_active:
            time.sleep(.03)
        left_click_lock_active = block_other_click_spam
        while keyboard.is_pressed('ctrl+shift'):
            left_click()
            time.sleep(click_delay)
        left_click_lock_active = False


@error_handler
def auto_click_right():
    global right_click_lock_active, left_click_lock_active
    while True:
        while (not (win32api.GetKeyState(0x02) not in (1, 0, -1) and keyboard.is_pressed(
                'ctrl+shift'))) or left_click_lock_active:
            time.sleep(.03)
        right_click_lock_active = block_other_click_spam
        while keyboard.is_pressed('ctrl+shift'):
            right_click()
            time.sleep(click_delay)
        right_click_lock_active = False


right_click_lock_active = False
left_click_lock_active = False
survival_activated = False
blacklist = {i.lower() for i in blacklist}
explicit_whitelist = {i.lower() for i in explicit_whitelist}

if __name__ == "__main__":
    # Keybindings
    keyboard.add_hotkey('ctrl+ü', toggle_game_close)
    keyboard.add_hotkey('ctrl+shift+ü', exit_script)
    keyboard.add_hotkey('ctrl+´', minimize_blacklisted)
    keyboard.add_hotkey("p", take_pic)
    keyboard.add_hotkey("v", toggle_survival)

    # permanent infinite loops
    threads = list()
    threads.append(threading.Thread(target=auto_click_left))
    threads.append(threading.Thread(target=auto_click_right))
    threads.append(threading.Thread(target=survive))
    for thread in threads:
        thread.start()

    # just run forever
    while True:
        time.sleep(1)
