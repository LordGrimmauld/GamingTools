import tkinter
import win32api
import win32con
import pywintypes
import keyboard
import win32gui


def toggle_black_screen(widget):
    global globalExStyle, label, old_hwnd, new_hwnd, cycle
    cycle += 1
    if cycle % 3 == 2:
        return
    globalExStyle ^= win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE
    switch = globalExStyle & (win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE)
    win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, globalExStyle)
    widget.master.wm_attributes("-transparentcolor", "black" if switch else "green")
    if not switch:
        old_hwnd = win32gui.GetForegroundWindow()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 10, 10, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 10, 10, 0, 0)
    else:
        win32gui.SetForegroundWindow(old_hwnd)


old_hwnd = win32gui.GetForegroundWindow()
cycle = 0
label = tkinter.Label(text=' ', font=('Times New Roman', '12'), fg='black', bg="black")
label.config(width=360, height=120, cursor="none")
label.master.overrideredirect(True)
label.master.geometry("+0+0")
label.master.lift()
label.master.wm_attributes("-topmost", True)
label.master.wm_attributes("-transparentcolor", "black")
label.bind("<Button-1>", lambda event: toggle_black_screen(event.widget))
hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
globalExStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, globalExStyle)
label.pack()
keyboard.add_hotkey("ctrl+shift+e", callback=toggle_black_screen, args=(label,))
win32gui.SetForegroundWindow(old_hwnd)
label.mainloop()
