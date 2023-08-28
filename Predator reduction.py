import os
import time
import pyautogui
import enum
import random
import asyncio
import cv2 as cv
import numpy as np
import requests
import pydirectinput

from windowcapture import WindowCapture
from windowmanager import WindowMgr
from vision import Vision


# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Global variables
Predator_icon = Vision('Predator.jpg')
reduction_button = Vision('AetherialReduction.jpg')
close_button = Vision('Close.jpg')


def runBot():

    # Change the working directory to the folder this script is in.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Focus on FFXIV
    w = WindowMgr()
    w.find_window(None, 'FINAL FANTASY XIV')
    w.set_foreground()

    # Initialize window capturing and event to compare to
    wincap = WindowCapture('FINAL FANTASY XIV')

    pydirectinput.keyDown('alt')

    while(True):

        screenshot = wincap.get_screenshot()
        predator = Predator_icon.find(
            screenshot, 0.7, 'rectangles')

        if predator:

            print(predator)
            print(predator[0][0])
            print(predator[0][1])
            pyautogui.moveTo(predator[0][0], predator[0]
                             [1]+random.randint(12, 16), 0.3, pyautogui.easeInQuad)
            pyautogui.rightClick()
            time.sleep(random.uniform(.15, .3))
            pyautogui.click(clicks=2, interval=0.1)
            time.sleep(random.uniform(.15, .3))

            screenshot = wincap.get_screenshot()
            reduction = reduction_button.find(
                screenshot, 0.7, 'rectangles')

            pyautogui.moveTo(reduction[0][0], reduction[0]
                             [1]+random.randint(24, 28), 0.3, pyautogui.easeInQuad)
            time.sleep(random.uniform(.15, .3))
            pyautogui.click(clicks=2, interval=0.1)

            time.sleep(random.uniform(3, 3.5))

        else:
            exit()


runBot()
# find predators
# pick any predator

# right click predator
# click aetherial reduction
# wait for reduction

# repeat until no predators are found
