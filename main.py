import time
import numpy as np
import cv2
import pyautogui
import tkinter as tk
from threading import Thread
import keyboard

# Load the target image you want to search for
target_image = cv2.imread('target_image.png')

# Define the region of the screen to capture
# Adjust the coordinates to fit the League of Legends client's window
capture_region = (0, 0, 1920, 1080)

# Define the threshold for image matching
threshold = 0.6

# Function to check if the target image is found on the screen
def is_image_on_screen():
    screenshot = pyautogui.screenshot(region=capture_region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    target_height, target_width, _ = target_image.shape
    for scale in np.arange(0.1, 2.1, 0.1):
        resized_target = cv2.resize(target_image, (int(target_width * scale), int(target_height * scale)))
        if resized_target.shape[0] > screenshot.shape[0] or resized_target.shape[1] > screenshot.shape[1]:
            continue  # Skip if the resized target is larger than the screenshot

        result = cv2.matchTemplate(screenshot, resized_target, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            return True

    return False

# Function to start the detection process
def start_detection():
    detecting.set(True)
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    detection_status.config(text="Detection: ON")
    Thread(target=detect).start()

# Function to stop the detection process
def stop_detection():
    detecting.set(False)
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    detection_status.config(text="Detection: OFF")

# Function for the detection loop
def detect():
    while detecting.get():
        if is_image_on_screen():
            # Image found, perform actions (e.g., click "ready" button)
            pyautogui.click(956, 712)  # Replace x and y with the coordinates of the "ready" button
            time.sleep(1)  # Wait for the action to be processed
        else:
            time.sleep(1)  # No match found, wait for the next check

# Create the GUI
window = tk.Tk()
window.title("Match Detection App")

# Create the GUI components
detecting = tk.BooleanVar(value=False)
start_button = tk.Button(window, text="Start Detecting", command=start_detection)
stop_button = tk.Button(window, text="Stop Detecting", command=stop_detection, state=tk.DISABLED)
detection_status = tk.Label(window, text="Detection: OFF")

# Function to start the detection when F6 is pressed
def start_detection_shortcut(event=None):
    start_detection()

# Function to stop the detection when F7 is pressed
def stop_detection_shortcut(event=None):
    stop_detection()

# Bind keyboard shortcuts using the keyboard library
keyboard.add_hotkey('F6', start_detection_shortcut)
keyboard.add_hotkey('F7', stop_detection_shortcut)

# Pack the GUI components
start_button.pack()
stop_button.pack()
detection_status.pack()

# Start the GUI event loop
window.mainloop()
