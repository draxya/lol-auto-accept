import time
import numpy
import cv2
import pyautogui

# Load the target image you want to search for
target_image = cv2.imread('target_image.png')

# Define the region of the screen to capture
# Adjust the coordinates to fit the League of Legends client's window
capture_region = (0, 0, 1920, 1080)

# Define the threshold for image matching
threshold = 0.8

# Function to check if the target image is found on the screen
def is_image_on_screen():
    screenshot = pyautogui.screenshot(region=capture_region)
    screenshot = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)

    result = cv2.matchTemplate(screenshot, target_image, cv2.TM_CCOEFF_NORMED)
    locations = numpy.where(result >= threshold)

    return len(locations[0]) > 0

# Main loop
while True:
    if is_image_on_screen():
        # Image found, perform actions (e.g., click "ready" button)
        pyautogui.click(956, 712)  # Replace x and y with the coordinates of the "ready" button
        time.sleep(1)  # Wait for the action to be processed
    else:
        time.sleep(1)  # No match found, wait for the next check
