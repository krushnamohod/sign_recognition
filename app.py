import cv2  # OpenCV for image processing and video capture
import mediapipe as mp  # Mediapipe for real-time hand tracking
import pyautogui as pag  # PyAutoGUI for controlling mouse/keyboard actions
from math import hypot  # For calculating the Euclidean distance between points
from scipy.interpolate import interp1d  # For remapping values smoothly
from ctypes import cast, POINTER  # Used for interacting with system audio
from comtypes import CLSCTX_ALL  # Required for system audio interaction
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # For controlling system volume
import numpy as np  # Used for numerical operations
from pynput.keyboard import Controller  # For simulating keyboard presses
import keyboard  # Another library for keyboard interactions
import webbrowser  # For opening URLs in the browser

############## Initialization ##############

cap = cv2.VideoCapture(0)  # Use scrcpy's mirrored screen as input
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

mpHands = mp.solutions.hands # Load Mediapipe Hands module
hands = mpHands.Hands(min_detection_confidence=0.70, min_tracking_confidence=0.70)
mpDraw = mp.solutions.drawing_utils #draw landmarks on the detected hand.

# Audio volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]

# Constants and variables
lms = [4, 8, 12, 16, 20]  # Key landmarks for fingers
volBar = 400  # Initial position of the volume bar


############## Utility ##############

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
    elif fingers == [False, False, True, False, False]:
        return "MIDDLE"
    elif fingers == [False, True, True, False, False]:
        return "VICTORY"
    elif fingers == [False, True, False, False, True]:
        return "SWAG"
    return "NONE"


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

netflix_opened=False
youtube_opened=False

############## Main ##############

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
            pag.scroll(-25)
        elif gesture == "FIST":
            pag.scroll(25)
        elif gesture == "VICTORY":
            if not netflix_opened:
                webbrowser.open("https://www.netflix.com")
                netflix_opened = True
            
        elif gesture == "SWAG":
            if not youtube_opened:
                webbrowser.open("https://www.youtube.com")
                youtube_opened = True
            

    # Volume bar visualization
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), -1)
    
    cv2.imshow("Hand Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
