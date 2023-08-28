import os
import time
import pyautogui
import enum
import random
import threading
import asyncio
import cv2 as cv
import numpy as np

from keybindings import KeyBindings
from windowcapture import WindowCapture
from windowmanager import WindowMgr
from vision import Vision
from fishingstatus import FishingStatus

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Global variables
exclamation_mark = Vision('ExclamationMark.jpg')
error_fish_got_away = Vision('ErrorFishGotAway.jpg')
error_lost_bait = Vision('LostBait.jpg')
error_try_new_location = Vision('TryNewLocation.jpg')
successful_catch = Vision('SuccessfulCatch.jpg')
patience = Vision('Patience.jpg')
total_GP = 737
patience_cost = 200
special_hook_cost = 50
regen_GP = 2
seconds = 60


# Set Patience if enough GP exists. Patience lasts for 60 seconds, set timeout. Patience costs 200 GP. Set a status to patience. In the meantime, keep track of GP slowly being regenerated (3sec = 7GP)
# While Patience is on and at least 50 GP exists, keep casting special hook. This follows regular cast/reeling guidelines.
# Patience is lost after 60 seconds, if status === specialHook then don't exit till result.
# Patience is lost after 60 seconds, if status != specialHook then exit safely.


def set_timeout(seconds, callback, arguments):
    return threading.Timer(seconds, callback, arguments)


def set_timer(callback=None):
    time = 60

    def countdown(time):
        time = time - 1
        if callback:
            callback()

    if time != 0:
        set_timeout(1, countdown, (time))


def special_cast(isCasting):
    pyautogui.press(KeyBindings.get('SpecialHook'))
    return True


async def cast_patience():
    if total_GP > 400:
        status = await press_button(KeyBindings.get('Patience'), status)

    if (status == FishingStatus.Patience):
        isSpecialCasting = False
        while (total_GP < 200 or status == FishingStatus.Patience):
            if (isSpecialCasting == False):
                isSpecialCasting = special_cast(isSpecialCasting)
            else:


def set_status(keypress, status):
    if keypress == KeyBindings.get('Cast'):
        status = FishingStatus.Fishing
    elif keypress == KeyBindings.get('Bait'):
        status = FishingStatus.ChangeBait
    elif keypress == KeyBindings.get('Reel'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('Quit'):
        status = FishingStatus.Exit
    elif keypress == KeyBindings.get('Patience'):
        status = FishingStatus.Patience
    return status


async def press_button(keypress, status):
    pyautogui.press(keypress)
    await asyncio.sleep(3)
    status = set_status(keypress, status)
    return status


async def reelInFish(currScreenShot, status):
    status = await press_button(KeyBindings.get('Reel'), status)
    return status


async def init(status, wincap):
    status = await press_button(KeyBindings.get('Cast'), status)
    screenshot = wincap.get_screenshot()
    new_location = error_try_new_location.find(screenshot, 0.7, 'rectangles')

    if new_location:
        cv.destroyAllWindows()
        exit()

    if ()
    return status


def runBot():
    # Change the working directory to the folder this script is in.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    status = FishingStatus.Idle

    # Focus on FFXIV
    w = WindowMgr()
    w.find_window(None, 'FINAL FANTASY XIV')
    w.set_foreground()

    # Initialize window capturing and event to compare to
    wincap = WindowCapture('FINAL FANTASY XIV')

    while(True):
        # Cast your line
        status = asyncio.run(init(status, wincap))

        if status == FishingStatus.Fishing:
            while status == FishingStatus.Fishing:
                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_found = exclamation_mark.find(
                    screenshot, 0.7, 'rectangles')

                if fish_found:
                    # Reel in fish and recast your line.
                    status = asyncio.run(reelInFish(screenshot, status))

                print(status)

        if status == FishingStatus.Reeling:
            while status == FishingStatus.Reeling:
                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.7, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.7, 'rectangles')
                success = successful_catch.find(
                    screenshot, 0.7, 'rectangles')

                print(status)
                if fish_got_away:
                    status = FishingStatus.Failure

                if lost_bait:
                    status = FishingStatus.Failure

                if success:
                    status = FishingStatus.Success

        print(status)

        if status == FishingStatus.Failure:
            time.sleep(1)
            continue
        elif status == FishingStatus.Success:
            time.sleep(2)
            continue
        elif status == FishingStatus.ChangeLocation:
            # Go to a different location
            exit()
        elif status == FishingStatus.Exit:
            exit()
        elif status == FishingStatus.ChangeBait:
            # Change bait
            exit()
        elif status == FishingStatus.Idle:
            exit()


runBot()
