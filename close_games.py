'''
Idea of this Script:
You want to minimize your game when people come in to your room?
You need a fast script that can detect the name of your window and instantly minimizes it on the press of a single button.
This button is currently bound to n, it can be rebound.
However, it is anoying if you want to type in the in-game chat and your game minimizes.
Therefore, a lock was added so this programm can be turned of temporarily.
This lock is bound to ctrl+ü, but as ü is a german-specific character, you as user of this script will have to rebind that key.
To completely exit_script this script, use ctrl+shift+ü (can be rebound as well)

This script uses the keyboard python-library. It has to be seperately installed by moving to your python folder, opening a command prompt and typing "python -m pip install keyboard"

This script is tested with Python37 only. It should in theory work on other versions of python, but that can not be guaranteed.

This script uses wintypes, windll, win32con and win32gui. Therefore, this script is (for now) only working on windows machines.

Further developement: As I did once do an alarm minimizing my windows whenever the door opened by applying a reed switch on the frame and a magnet on the door and connecting that to an arduino, there will be a second version of this script activated from USB serial input.


Made by: Grimmauld
'''
import keyboard  # You will have to install this lib
import sys
from ctypes import wintypes, windll, create_unicode_buffer
import win32con
import win32gui

lock = False  # start of the lock (depending on your application, change this to True)
blacklist = {"diep", "youtube", "minecraft"}  # everything you want to block, add your own games here.

def minimizeForbidden():
    if not lock:  # check the lock
        return
    hWnd = windll.user32.GetForegroundWindow()  # get foreground window
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)  # read the title
    if buf.value is not None and any(map(lambda x: x in buf.value, blacklist)):  # is any of the blacklisted items contained in the active windows title?
        win32gui.ShowWindow(hWnd, win32con.SW_MINIMIZE)

def toggle():  # toggle_game_close the lock and give a message about the new status in the console.
    global lock
    lock = not lock
    print("Lock is now " + ("active" if lock else "inactive"))

def exit():  # give a message while exiting.
    print("exiting now...")
    sys.exit()


# Keybindings
keyboard.add_hotkey('ctrl+ü', toggle)
keyboard.add_hotkey('ctrl+shift+ü', exit)
keyboard.add_hotkey('n', minimizeForbidden)
