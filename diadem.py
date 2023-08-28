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
import pydirectinput

from keybindings import KeyBindings
from windowcapture import WindowCapture
from windowmanager import WindowMgr
from vision import Vision
from fishingstatus import FishingStatus

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Global variables
exclamation_mark = Vision('ExclamationMark1.jpg')
error_fish_got_away = Vision('ErrorFishGotAway1.jpg')
error_lost_bait = Vision('LostBait2.jpg')
error_try_new_location = Vision('TryNewLocation.jpg')
error_nothing = Vision('NothingBites1.jpg')
successful_catch = Vision('SuccessfulCatch1.jpg')
patience = Vision('Patience.jpg')
mana_full = Vision('FullGP.jpg')
mana_low = Vision('LowGP1.jpg')
cordial_available = Vision('CordialAvailable.jpg')
collectable = Vision('Yes.jpg')
mooch = Vision('Mooch1.jpg')
mooch2 = Vision('Mooch2.jpg')
mooch2up = Vision('Mooch2Available.jpg')
doublehook = Vision('DoubleHookAvailable.jpg')

# settings to edit

UseCordial = True
MoochFish = True
UsePatience = True
useDoubleHook = False

# starting assignments

isPatienceCast = False
isDoubleHookAvailable = False
repeat = 0

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
        status = FishingStatus.Mooching
    elif keypress == KeyBindings.get('Mooch2'):
        status = FishingStatus.Mooching
    elif keypress == KeyBindings.get('Reel'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('Quit'):
        status = FishingStatus.Exit
    elif keypress == KeyBindings.get('PrecisionHook'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('PowerfulHook'):
        status = FishingStatus.Reeling
    elif keypress == KeyBindings.get('DoubleHook'):
        status = FishingStatus.Reeling
    return status


async def press_button(keypress, status):
    pyautogui.press(keypress)
    await asyncio.sleep(random.uniform(0.2, 0.4))
    status = set_status(keypress, status)
    return status


async def reelInFish(currScreenShot, status):
    global isPatienceCast
    global useDoubleHook
    global isDoubleHookAvailable

    if isPatienceCast and status == FishingStatus.Mooching:
        status = await press_button(KeyBindings.get('PowerfulHook'), status)
    elif isPatienceCast:
        status = await press_button(KeyBindings.get('PrecisionHook'), status)
    elif useDoubleHook and isDoubleHookAvailable:
        status = await press_button(KeyBindings.get('DoubleHook'), status)
    else:
        status = await press_button(KeyBindings.get('Reel'), status)
    return status


async def init(status, wincap):
    global isPatienceCast
    global UseCordial
    global repeat
    global MoochFish

    screenshot = wincap.get_screenshot()
    is_mana_full = mana_full.find(screenshot, 0.8, 'rectangles')
    is_patience_on = patience.find(screenshot, 0.9, 'rectangles')
    moochable = mooch.find(screenshot, 0.9, 'rectangles')
    mooch2able = mooch2.find(screenshot, 0.9, 'rectangles')
    mooch2available = mooch2up.find(screenshot, 0.9, 'rectangles')

    await asyncio.sleep(random.uniform(0.4, 0.8))

    if moochable and MoochFish:
        status = await press_button(KeyBindings.get('Mooch'), status)

    if mooch2able and MoochFish and mooch2available:
        status = await press_button(KeyBindings.get('Mooch2'), status)

    if is_patience_on:
        isPatienceCast = True
    else:
        isPatienceCast = False

    await asyncio.sleep(random.uniform(0.4, 0.8))

    if is_mana_full and (isPatienceCast == False) and UsePatience:
        pyautogui.press((KeyBindings.get('Patience')))
        isPatienceCast = True
        print('using patience')

    screenshot3 = wincap.get_screenshot()
    is_mana_low = mana_low.find(screenshot3, 0.9, 'rectangles')
    is_cordial_available = cordial_available.find(
        screenshot3, 0.8, 'rectangles')

    await asyncio.sleep(random.uniform(0.4, 0.8))

    if is_mana_low and is_cordial_available and UseCordial:
        pyautogui.press((KeyBindings.get('Cordial')))
        print('using cordial')

    await asyncio.sleep(random.uniform(0.4, 0.8))

    if status == (FishingStatus.Mooching):
        pass
    elif status != (FishingStatus.Fishing):
        status = await press_button(KeyBindings.get('Cast'), status)

    screenshot2 = wincap.get_screenshot()
    new_location = error_try_new_location.find(screenshot2, 0.6, 'rectangles')
    print(new_location)

    if new_location and (repeat >= 0):
        cv.destroyAllWindows()
        test = telegram_bot_sendtext("done")
        exit()

    if new_location and (repeat < 1):
        # enter auto run key
        time.sleep(2)

        pydirectinput.keyDown('up')
        time.sleep(7)
        pydirectinput.keyUp('up')

        repeat = repeat + 1

        status = await press_button(KeyBindings.get('Cast'), status)

    return status


def runBot():
    global status
    global isPatienceCast
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

            timeout = time.time() + 9

            while status == FishingStatus.Fishing:
                # Capture a screenshot and check to see if event has been triggered.
                now = time.time()
                screenshot = wincap.get_screenshot()
                fish_found = exclamation_mark.find(
                    screenshot, 0.7, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.9, 'rectangles')
                is_patience_on = patience.find(screenshot, 0.9, 'rectangles')
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.9, 'rectangles')
                nothing = error_nothing.find(screenshot, 0.9, 'rectangles')
                doublehook_opportunity = doublehook.find(
                    screenshot, 0.9, 'rectangles')

                if is_patience_on:
                    isPatienceCast = True
                else:
                    isPatienceCast = False

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
                    status = FishingStatus.Failure

        if status == FishingStatus.Mooching:
            while status == FishingStatus.Mooching:
                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_found = exclamation_mark.find(
                    screenshot, 0.65, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.9, 'rectangles')
                is_patience_on = patience.find(screenshot, 0.9, 'rectangles')
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.9, 'rectangles')
                nothing = error_nothing.find(screenshot, 0.9, 'rectangles')
                doublehook_opportunity = doublehook.find(
                    screenshot, 0.9, 'rectangles')

                if is_patience_on:
                    isPatienceCast = True
                else:
                    isPatienceCast = False

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

        if status == FishingStatus.Reeling:
            while status == FishingStatus.Reeling:
                # Capture a screenshot and check to see if event has been triggered.
                screenshot = wincap.get_screenshot()
                fish_got_away = error_fish_got_away.find(
                    screenshot, 0.9, 'rectangles')
                success = successful_catch.find(screenshot, 0.9, 'rectangles')
                confirm_collectable = collectable.find(
                    screenshot, 0.7, 'rectangles')
                lost_bait = error_lost_bait.find(
                    screenshot, 0.9, 'rectangles')
                moochable = mooch.find(screenshot, 0.9, 'rectangles')
                nothing = error_nothing.find(screenshot, 0.9, 'rectangles')

                print(status)

                if fish_got_away:
                    status = FishingStatus.Failure

                elif lost_bait:
                    status = FishingStatus.Failure

                elif nothing:
                    status = FishingStatus.Failure

                elif confirm_collectable:
                    time.sleep(random.uniform(.5, 1))
                    pyautogui.moveTo(random.randint(888, 958), random.randint(
                        620, 629), 0.3, pyautogui.easeInQuad)
                    pyautogui.click(clicks=2, interval=0.1)
                    time.sleep(random.uniform(.5, 1))
                    status = FishingStatus.Success

                elif moochable:
                    status = FishingStatus.Success

                elif success:
                    status = FishingStatus.Success

        print(status)
        if isPatienceCast == True:
            print('Patience On')

        if status == FishingStatus.Failure:
            time.sleep(random.uniform(0.3, 0.7))
            continue
        elif status == FishingStatus.Success:
            time.sleep(random.uniform(.5, 1))
            continue
        elif status == FishingStatus.ChangeLocation:
            # Go to a different location
            test = telegram_bot_sendtext("done")
            exit()


runBot()
