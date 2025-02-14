# Hand Gesture Control System

## Overview
This project is a hand gesture control system that uses a webcam to recognize specific hand gestures and perform actions such as controlling system volume, scrolling, and opening websites like YouTube and Netflix. It leverages OpenCV, MediaPipe, and Pycaw for hand tracking and system interactions.

## Features
- **Hand Gesture Recognition**: Detects specific hand gestures to perform different actions.
- **Volume Control**: Increase or decrease system volume using gestures.
- **Scrolling**: Scroll up or down on a webpage using hand movements.
- **Web Navigation**: Open YouTube and Netflix using designated gestures.

## Setup
For this Project you will need python version from 3.10 to 3.12 (preferably python 3.11.9)
Paste this command to know your machines python version:
```bash
python --version # if it is more than 3.12 then paste following command in your terminal
winget install Python.Python --version 3.11.9 --force # only for windows
```
Before installing dependencies, create a virtual environment:
#### For Windows
```bash
python -m venv venv
venv\Scripts\activate
```
#### For Linux or MacOS
```bash
python -m venv venv # for Macos use python3 -m venv venv
source venv/bin/activate
```
If virtal environment is not installed, paste this command in your terminal:
```bash
pip install virtualenv
```

## Dependencies
Ensure you have the following dependencies installed before running the script:
```bash
pip install opencv-python mediapipe numpy pycaw pynput keyboard
```

## How It Works
1. The program uses OpenCV to capture video input from the webcam.
2. MediaPipe's hand tracking module detects hand landmarks.
3. Specific hand gestures are identified and mapped to system actions:
   - **Index Finger Up** → Increase Volume
   - **Thumb Up** → Decrease Volume
   - **Five Fingers Open** → Scroll Down
   - **Fist (Four Fingers Closed)** → Scroll Up
   - **Ring Finger Up** → Open Netflix
   - **Little Finger Up** → Open YouTube
4. Pycaw is used to adjust system volume.
5. PyAutoGUI and keyboard libraries are used for keyboard and mouse interactions.

## Usage
Run the script using:
```bash
python app.py
```
Use the designated hand gestures in front of the camera to control the system.

## Exit
Press `q` to exit the application.
OR
Press ctrl+c in the terminal  # for windows and linux
If your are on macos use command c

