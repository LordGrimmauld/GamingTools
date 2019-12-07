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


def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None


try:
    with open("highscores.json", "r") as f:
        highscores = json.load(f)
except FileNotFoundError as e:
    with open("highscores.json", "w") as f:
        json.dump({}, f)
        highscores = {}

click_delay = .005  # delay of autoclick-functionality
blockkeys = "wasdepuml1234567"  # keys that might block the combination of l + alt + prtscn
lock = True  # start of the lock (depending on your application, change this to True)
blacklist = {"diep", "youtube", "minecraft"}  # everything you want to block, add your own games here.
explicit_whitelist = {"pycharm",
                      "discord"}  # every thing you do not want to close, even though its title may contain game titles.


def error_handler(method):
    def tested(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            print(e)

    return tested


def take_pic():
    if "diep.io" in getForegroundWindowTitle():
        [keyboard.block_key(k) for k in blockkeys]
        keyboard.press("l")
        time.sleep(.1)
        keyboard.press_and_release("alt+prtscn")
        time.sleep(.05)
        keyboard.release("l")
        [keyboard.unblock_key(k) for k in blockkeys]
        time.sleep(.1)
        img = ImageGrab.grabclipboard()
        time.sleep(.1)
        img2 = img.crop((3 * img.width // 7, 13 * img.height // 14, 4 * img.width // 7, img.height))
        for x in range(img2.width):
            for y in range(img2.height):
                p = img2.getpixel((x, y))
                img2.putpixel((x, y), (0, 0, 0) if all(map(lambda x: x > 185, p)) and not all(
                    map(lambda x: 207 > x > 195, p)) and p not in [(198, 198, 198), (205, 205, 205),
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
            if _class in highscores:
                if _score > highscores[_class][0]:
                    if highscores[_class][1] in os.listdir("highscores"):
                        os.remove("highscores\\" + highscores[_class][1])
                else:
                    return
            filename = _class + "-" + str(_score) + "-" + datetime.now().strftime("%m~%d~%Y-%H~%M") + ".png"
            highscores[_class] = (_score, filename)
            img.save("highscores\\" + filename, "PNG")
            with open("highscores.json", "w") as f:
                json.dump(highscores, f)
        else:
            print(text)
            take_pic()  # Fixme: maybe not a good idea...
        # Imgur??? https://steemit.com/programming/@synapse/how-to-upload-images-to-imgur-using-python


survival = False


def toggle_survival():
    global survival
    if "diep.io" in getForegroundWindowTitle():
        survival = not survival
        print("survival mode", "activated" if survival else "deactivated")


def minimize_blacklisted():
    if not lock:  # check the lock
        return
    hWnd = windll.user32.GetForegroundWindow()  # get foreground window
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)  # read the title
    # print(buf.value)
    if buf.value is not None and any(map(lambda x: x in buf.value.lower(), blacklist)) and not any(
            map(lambda x: x in buf.value.lower(),
                explicit_whitelist)):  # is any of the blacklisted items contained in the active windows title?
        win32gui.ShowWindow(hWnd, win32con.SW_MINIMIZE)


def toggle_game_close():  # toggle_game_close the lock and give a message about the new status in the console.
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
        flags, hcursor, (x, y) = win32gui.GetCursorInfo()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def right_click(x=None, y=None):
    if x is not None and y is not None:
        win32api.SetCursorPos((x, y))
    else:
        flags, hcursor, (x, y) = win32gui.GetCursorInfo()
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)


@error_handler
def survive():
    n = 0
    while True:
        if survival and "diep.io" in getForegroundWindowTitle():
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
def autoclick_left():
    global left_click_lock_active, right_click_lock_active
    while True:
        while (not (win32api.GetKeyState(0x01) not in (1, 0, -1) and keyboard.is_pressed(
                'ctrl+shift'))) or right_click_lock_active:
            time.sleep(.03)
        left_click_lock_active = True
        while keyboard.is_pressed('ctrl+shift'):
            left_click()
            time.sleep(click_delay)
        left_click_lock_active = False


@error_handler
def autoclick_right():
    global right_click_lock_active, left_click_lock_active
    while True:
        while (not (win32api.GetKeyState(0x02) not in (1, 0, -1) and keyboard.is_pressed(
                'ctrl+shift'))) or left_click_lock_active:
            time.sleep(.03)
        right_click_lock_active = True
        while keyboard.is_pressed('ctrl+shift'):
            right_click()
            time.sleep(click_delay)
        right_click_lock_active = False


right_click_lock_active = False
left_click_lock_active = False
blacklist = {i.lower() for i in blacklist}
explicit_whitelist = {i.lower() for i in explicit_whitelist}

if __name__ == "__main__":
    # Keybindings
    keyboard.add_hotkey('ctrl+ü', toggle_game_close)
    keyboard.add_hotkey('ctrl+shift+ü', exit_script)
    keyboard.add_hotkey('ctrl+´', minimize_blacklisted)
    keyboard.add_hotkey("p", take_pic)
    keyboard.add_hotkey("v", toggle_survival)

    threads = []
    threads.append(threading.Thread(target=autoclick_left))
    threads.append(threading.Thread(target=autoclick_right))
    threads.append(threading.Thread(target=survive))
    for thread in threads:
        thread.start()
    keyboard.wait()
