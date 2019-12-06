import win32api
import win32con
import win32gui
import keyboard
import time

def click(x=None, y=None):
    if x is not None and y is not None:
        win32api.SetCursorPos((x,y))
    else:
        flags, hcursor, (x,y) = win32gui.GetCursorInfo()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


while True:
    while not (win32api.GetKeyState(0x01) not in (1, 0, -1) and keyboard.is_pressed('ctrl+shift')):
        time.sleep(.1)
    while keyboard.is_pressed('ctrl+shift'):
        click()
        time.sleep(.01)
