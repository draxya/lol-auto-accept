# lol-auto-accept
An application for LoL players to auto accept the match when a new one is found.

**Shortcuts:**
- F6: Start Detection
- F7: Stop Detection

## How does it work?
The program takes a screenshot of a LoL new match notification as base target image, and repeadetly looks for that image in screen and if finds, clicks to a certain area where "Accept Match" button is supposed to be.

## Note:
This application is optimized for 1080p resolution. If you are using another res, you can detect your "accept match" button's position with [Mouse Position Tracker](https://github.com/draxya/Mouse-Position-Tracker) and change the source code as is. In future developemnt, software is going to be relative to resolutions.

## Dependencies
- time
- numpy
- opencv-python
- pyautogui
- tkinter
- keyboard
