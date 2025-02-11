import cv2
import mediapipe as mp
import pyautogui as pag
from math import hypot
from scipy.interpolate import interp1d
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
from pynput.keyboard import Controller
import keyboard
############## Initialization ##############
  

cap = cv2.VideoCapture(0)  # Use scrcpy's mirrored screen as input

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.70, min_tracking_confidence=0.70)
mpDraw = mp.solutions.drawing_utils

# Audio volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]

# Constants and variables
lms = [4, 8, 12, 16, 20]  # Key landmarks for fingers
volBar = 400

############################################

# Utility functions
def getDistance(p1, p2):
    return hypot(p1[0] - p2[0], p1[1] - p2[1])

def detectGesture(fingers):
    if fingers == [False, True, False, False, False]:
        return "INDEX"  # Increase Volume
    elif fingers == [True, False, False, False, False]:
        return "THUMB"  # Decrease Volume
    elif fingers == [True, True, True, True, True]:
        return "FIVE"  # Pause
    elif fingers == [False, True, True, True, True]:
        return "FIST"  # Play
    return "NONE"

def keyBinding(res):
    try:
        if res == 'FIVE':
            pag.press('k')
        elif res == 'FIST':
            pag.press('l')
        elif res == 'INDEX':
            pag.press('right')
        elif res == 'THUMB':
            pag.press('left')
    except Exception as e:
        print(f"Error in key binding: {e}")

def remap(x, in_min, in_max, out_min, out_max, flag=0):
    if x > in_max:
        return out_max if flag == 1 else -63.5
    if x < in_min:
        return out_min if flag == 1 else 0.0
    try:
        m = interp1d([in_min, in_max], [out_min, out_max])
        return float(m(x))
    except Exception as e:
        print(f"Error in remapping: {e}")
        return 0.0

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to access the camera.")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:
            for lm in handlandmark.landmark:
                h, w, _ = img.shape
                lmList.append([int(lm.x * w), int(lm.y * h)])
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    if lmList:
        fingers = []
        if lmList[5][0] < lmList[17][0]:
            fingers.append(lmList[lms[0]][0] < lmList[lms[0] - 1][0])
        else:
            fingers.append(lmList[lms[0]][0] > lmList[lms[0] - 1][0])
        for lm in range(1, len(lms)):
            fingers.append(lmList[lms[lm]][1] < lmList[lms[lm] - 2][1])

        gesture = detectGesture(fingers)
        cv2.putText(img, gesture, (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

        if gesture == "INDEX":
            vol = volume.GetMasterVolumeLevel() + 0.4
            vol = min(vol, volMax)
            volume.SetMasterVolumeLevel(vol, None)
            volBar = remap(vol, volMin, volMax, 400, 150, 1)
        elif gesture == "THUMB":
            vol = volume.GetMasterVolumeLevel() - 0.4
            vol = max(vol, volMin)
            volume.SetMasterVolumeLevel(vol, None)
            volBar = remap(vol, volMin, volMax, 400, 150, 1)
        elif gesture == "FIVE":
            pass
            # keyboard.press('media_play_pause')  # This simulates a media pause/play toggle
            # keyboard.release('media_play_pause')
        elif gesture == "FIST":
            pass
            # keyboard.press('media_play_pause')  # This simulates a media pause/play toggle
            # keyboard.release('media_play_pause')

    # Volume bar visualization
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), -1)
    
    # Debug grid lines
    cv2.line(img, (320, 0), (320, 480), (237, 149, 100), 1)
    cv2.line(img, (0, 240), (640, 240), (237, 149, 100), 1)

    cv2.imshow("Hand Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()