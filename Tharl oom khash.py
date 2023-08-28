import os
import time
import pyautogui
import enum
import random
import threading
import asyncio
import cv2 as cv
import numpy as np
import requests

from keybindings import KeyBindings
from windowcapture import WindowCapture
from windowmanager import WindowMgr
from vision import Vision
from fishingstatus import FishingStatus

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Global variables
exclamation_mark = Vision('TripleMark.jpg')
error_fish_got_away = Vision('ErrorFishGotAway1.jpg')
error_lost_bait = Vision('LostBait2.jpg')
error_try_new_location = Vision('TryNewLocation.jpg')
error_nothing = Vision('NothingBites1.jpg')
successful_catch = Vision('SuccessfulCatch1.jpg')
patience = Vision('Patience.jpg')
mana_full = Vision('FullGP.jpg')
mana_low = Vision('LowGP.jpg')
cordial_available = Vision('CordialAvailable.jpg')
collectable = Vision('Yes.jpg')
doublehook = Vision('DoubleHookAvailable.jpg')

# settings to edit

UseCordial = False
useDoubleHook = True

# starting assignments

isPatienceCast = False
isDoubleHookAvailable = False

# set up telegram bot for alerts when fishing stops as a result of fish sensing something amiss


def telegram_bot_sendtext(bot_message):

    bot_token = '1381642281:AAFXpAg6Vbu3BGJVGOOSeLsN34kQO9SCLv4'
    bot_chatID = '1113836411'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def set_status(keypress, status):
    if keypress == KeyBindings.get('Cast'):
        status = FishingStatus.Fishing
    elif keypress == KeyBindings.get('Mooch'):
        status = FishingStatus.Fishing
    elif keypress == KeyBindings.get('Reel'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('Quit'):
        status = FishingStatus.Failure
    elif keypress == KeyBindings.get('SpecialHook'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('DoubleHook'):
        status = FishingStatus.Reeling
    return status


async def press_button(keypress, status):
    pyautogui.press(keypress)
    await asyncio.sleep(random.uniform(0.4, 0.8))
    status = set_status(keypress, status)
    return status


async def reelInFish(currScreenShot, status):

    global useDoubleHook
    global isDoubleHookAvailable

    if useDoubleHook and isDoubleHookAvailable:
        status = await press_button(KeyBindings.get('DoubleHook'), status)
    else:
        status = await press_button(KeyBindings.get('Reel'), status)
    return status


async def init(status, wincap):

    global UseCordial

    screenshot3 = wincap.get_screenshot()
    is_mana_low = mana_low.find(screenshot3, 0.9, 'rectangles')
    is_cordial_available = cordial_available.find(
        screenshot3, 0.8, 'rectangles')

    print(is_mana_low)

    if is_mana_low and is_cordial_available and UseCordial:
        pyautogui.press((KeyBindings.get('Cordial')))
        print('using cordial')

    if status != FishingStatus.Fishing:
        status = await press_button(KeyBindings.get('Cast'), status)

    screenshot2 = wincap.get_screenshot()
    new_location = error_try_new_location.find(screenshot2, 0.7, 'rectangles')

    if new_location:
        cv.destroyAllWindows()
        test = telegram_bot_sendtext("done")
        exit()

    return status


def runBot():
    global status
    global isDoubleHookAvailable

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
            timeout = time.time() + 8

            while status == FishingStatus.Fishing:

                now = time.time()

                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_found = exclamation_mark.find(
                    screenshot, 0.6, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.9, 'rectangles')
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.9, 'rectangles')
                nothing = error_nothing.find(screenshot, 0.9, 'rectangles')
                doublehook_opportunity = doublehook.find(
                    screenshot, 0.9, 'rectangles')

                if doublehook_opportunity:
                    isDoubleHookAvailable = True
                else:
                    isDoubleHookAvailable = False

                print(status)

                if fish_found:
                    # Reel in fish and recast your line.
                    status = asyncio.run(reelInFish(screenshot, status))

                elif fish_got_away:
                    status = FishingStatus.Failure
                elif lost_bait:
                    status = FishingStatus.Failure
                elif nothing:
                    status = FishingStatus.Failure
                elif now > timeout:
                    pyautogui.press((KeyBindings.get('Reel')))
                    time.sleep(random.uniform(1.5, 2))
                    status = FishingStatus.Failure

        if status == FishingStatus.Reeling:
            while status == FishingStatus.Reeling:
                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.9, 'rectangles')
                success = successful_catch.find(screenshot, 0.9, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.9, 'rectangles')
                nothing = error_nothing.find(screenshot, 0.9, 'rectangles')

                print(status)

                if fish_got_away:
                    status = FishingStatus.Failure

                elif lost_bait:
                    status = FishingStatus.Failure

                elif nothing:
                    status = FishingStatus.Failure

                elif success:
                    status = FishingStatus.Success

        print(status)

        if status == FishingStatus.Failure:
            time.sleep(random.uniform(0.3, 0.7))
            continue
        elif status == FishingStatus.Success:
            time.sleep(random.uniform(1, 1.5))
            continue
        elif status == FishingStatus.ChangeLocation:
            # Go to a different location
            test = telegram_bot_sendtext("done")
            exit()


runBot()
