import tkinter
import win32api
import win32con
import pywintypes
import keyboard
from ctypes import wintypes
import ctypes
user32 = ctypes.WinDLL("user32")


user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = (
    wintypes.LPCWSTR, # lpClassName
    wintypes.LPCWSTR) # lpWindowName

user32.ShowWindow.argtypes = (
    wintypes.HWND, # hWnd
    ctypes.c_int)  # nCmdShow


def hide_taskbar():
    hWnd = user32.FindWindowW(u"Shell_traywnd", None)
    user32.ShowWindow(hWnd, 0)

def unhide_taskbar():
    hWnd = user32.FindWindowW(u"Shell_traywnd", None)
    user32.ShowWindow(hWnd, 5)


def toggle_black_screen(widget):
    global globalExStyle, label, old_hwnd, new_hwnd
    globalExStyle ^= win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE
    switch = globalExStyle & (win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE)
    win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, globalExStyle)
    widget.master.wm_attributes("-transparentcolor", "black" if switch else "green")
    if switch:
        unhide_taskbar()
    else:
        hide_taskbar()


label = tkinter.Label(text=' ', font=('Times New Roman', '12'), fg='black', bg="black")
label.config(width=360, height=120, cursor="none")
label.master.overrideredirect(True)
label.master.geometry("+0+0")
label.master.lift()
label.master.wm_attributes("-topmost", True)
label.master.wm_attributes("-transparentcolor", "black")
label.bind("<Button-1>", lambda event: toggle_black_screen(event.widget))
hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
globalExStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, globalExStyle)
label.pack()
keyboard.add_hotkey("ctrl+shift+e", callback=toggle_black_screen, args=(label,))
label.mainloop()
