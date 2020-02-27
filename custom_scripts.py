import keyboard
import time
import re
import win32api
import win32gui
import win32con
from ctypes import windll


def record_hotkey():
    max_len = 0
    keypress = ""
    while not keyboard.get_hotkey_name():
        time.sleep(.01)
    _n = keyboard.get_hotkey_name()
    while _n:
        if len(_n.split("+")) > max_len:
            max_len = len(_n.split("+"))
            keypress = _n
        time.sleep(.01)
        _n = keyboard.get_hotkey_name()
    return keyboard.normalize_name(keypress)


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


def call_keysequence(seq_string, delay=.05, call_after=0):
    time.sleep(call_after)
    return parse_keysequence(seq_string, delay, True, windll.user32.GetForegroundWindow())


def parse_keysequence(sequence_string, delay=.05, called_first=False, hwnd=None):
    # * -> loop forever
    # ^n -> loop n times
    # () -> execute inner
    # [] -> literal key (shift, left shift, enter, ctrl, ^, 45, ...) (no brackets though!)
    # & -> press down (before key)
    # ! -> up (before key)
    # !! -> release all
    # . -> left click
    # , -> right click
    k = 0
    x = 0
    i = 0
    pressed = set()
    hold = False
    release = False
    while i < len(sequence_string) and (
            hwnd is None or hwnd == windll.user32.GetForegroundWindow()) and not keyboard.is_pressed("esc"):
        if sequence_string[i] not in "[]{},.^1234567890*()&!":
            k = sequence_string[i]
            if release:
                keyboard.release(k)
                pressed.remove(k)
                release = False
            elif hold:
                keyboard.press(k)
                pressed.add(k)
                hold = False
            else:
                keyboard.press_and_release(k)
            time.sleep(delay)
        elif sequence_string[i] == "&":
            hold = True
        elif sequence_string[i] == "!":
            if not release:
                release = True
            else:
                for k in pressed:
                    keyboard.release(k)
                pressed = set()
        elif sequence_string[i] == "[":
            i += sequence_string[i:].index("]")
            continue
        elif sequence_string[i] == "]":
            k = sequence_string[i - [*reversed(sequence_string[:i])].index("["):i]
            if release:
                keyboard.release(k)
                pressed.remove(k)
                release = False
            elif hold:
                keyboard.press(k)
                pressed.add(k)
                hold = False
            else:
                keyboard.press_and_release(k)
            time.sleep(delay)
        elif sequence_string[i] == "*":
            i -= 1
            continue
        elif sequence_string[i] == ".":
            left_click()
            time.sleep(delay)
        elif sequence_string[i] == ",":
            right_click()
            time.sleep(delay)
        elif sequence_string[i] == "^":
            if k < int(sequence_string[i + 1:i + 1 + re.search("[0-9]*", sequence_string[i + 1:]).span()[1]]) - 1:
                k += 1
                i -= 1
                continue
            else:
                k = 0
        elif sequence_string[i] == "(":
            _n = 0
            i += 1
            x = i
            while sequence_string[i] != ")" or _n:
                if sequence_string[i] == "(":
                    _n += 1
                elif sequence_string[i] == ")":
                    _n -= 1
                i += 1
            continue
        elif sequence_string[i] == ")":
            parse_keysequence(sequence_string[x:i], delay)
        i += 1
    if called_first:
        for k in pressed:
            keyboard.release(k)
    return 0

# call_keysequence("&w([8],[9],)*", .05, 5)
