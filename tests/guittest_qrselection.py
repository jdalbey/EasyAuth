import os
import threading
import time
import subprocess
from pathlib import Path

import pyautogui as gui
from PIL import Image

# Test script to exercise the QR Selection dialog

def start_app():
    root = os.getcwd()
    arg1 = root + "/tests/test_data/config_test1.ini"
    # start EasyAuth with a custom config file that points to a test directory for the vault
    process = subprocess.Popen(['python3', 'src/main.py', '-c', arg1],
        stdout=subprocess.PIPE,  # Capture standard output
        stderr=subprocess.PIPE   # Capture standard error
    )
    return process

def drive_with_pyautogui():

    gui.PAUSE = 0.5  # sec after each command
    gui.FAILSAFE = True
    # Wait for the app to start
    time.sleep(1)

def capture_output(process):
    # Capture stdout and stderr from the process
    stdout, stderr = process.communicate()  # Wait for process to finish and capture output
    if stdout:
        print("Standard Output:")
        print(stdout.decode())  # Decode bytes to string
    if stderr:
        print("Standard Error:")
        log_results = stderr.decode()  # Decode bytes to string
        print (log_results)
        # verify account was updated correctly
        assert log_results.strip().endswith("LinkedIn (earthling@planet.com)")

def find_and_close_image_window():
    # Using wmctrl to find windows by title
    try:
        # List all windows and find the one that matches your criteria
        windows = subprocess.check_output(['wmctrl', '-l']).decode('utf-8')
        for line in windows.splitlines():
            window = line.lower()
            if ' tmp' in window and '.png' in window:  # search term
                print (f"Closing {window}")
                window_id = line.split()[0]
                subprocess.run(['wmctrl', '-ic', window_id])

    except subprocess.CalledProcessError:
        print("Error using wmctrl")

# Schedule a function to press the Scan button after the image is shown
def grab_code():
    # Look for the image
    print ("Looking for image")
    gui.hotkey('alt','s')       # click "Scan" button
    # Selection dialog should appear
    time.sleep(1)
    gui.hotkey('alt','1')       # click first radio button
    gui.hotkey('alt','o')       # click OK
    time.sleep(1)               # Pause for human verification
    # close the window with the qr code
    find_and_close_image_window()
    # display should show new account
    time.sleep(1)

    # Exit Application
    gui.hotkey('alt', 'x')
    print("done")

def show_image():
    print ("Starting countdown")
    threading.Timer(1.5, grab_code).start()
    # Display a QR code from a test file
    image_file = 'tests/test_data/img_qr_code_triple.png'
    image = Image.open(image_file)
    image.show()
    image.close()  # close file handle
    return image

if __name__ == "__main__":
    # For this test we make a vault in developer's home directory
    vault = os.path.join(Path.home(),os.path.normpath("vault.json"))
    if os.path.exists(vault):
        # Remove any prior artifacts
        os.remove(vault)

    # Execute `show_image()` after 0.5 seconds
    #threading.Timer(0.5, show_image).start()
    image = show_image()
    app_process = start_app()
    drive_with_pyautogui()
    # Optionally, wait for the application process to finish
    app_process.wait()
    # Capture and print the output from the application
    capture_output(app_process)
