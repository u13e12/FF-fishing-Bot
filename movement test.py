import pyautogui
import time
from windowmanager import WindowMgr
import pydirectinput

w = WindowMgr()
w.find_window(None, 'FINAL FANTASY XIV')
w.set_foreground()

pydirectinput.keyDown('up')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
time.sleep(.4)
pydirectinput.press('left')
pydirectinput.keyUp('up')
