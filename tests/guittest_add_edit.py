import os
import time
import subprocess
import pyautogui as gui

# Test Script to exercise Add and Edit dialogs, including Lookup

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

    # Press Add Account button
    #gui.mouseInfo()
    gui.hotkey('alt', 'a')                  # Open add dialog
    time.sleep(1)
    # Fill the form fields
    gui.typewrite("Woogle\tUser\tAB34")     # Manually complete fields
    gui.hotkey('alt','a')                   # click 'add'
    time.sleep(1)
    gui.press(['tab','tab','tab','space'])  # Open edit dialog
    gui.press('tab')                        # tab to user field
    gui.typewrite('User Bob')               # update user
    gui.hotkey('alt','s')                   # save & close

    gui.press(['tab','tab','tab','space'])  # Open edit dialog
    gui.hotkey('alt', 'l')                  # Open Lookup
    gui.typewrite('spring')                 # Enter name in search field
    gui.press('enter')                      # Accept
    gui.hotkey('alt', 'l')                  # Open Lookup
    gui.press(['down','down'])              # Browse the list
    gui.press('enter')                      # Accept
    gui.hotkey('alt','s')                   # save & close


    # Exit Application
    gui.hotkey('alt','x')
    print ("done")


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
        # verify account was updated to '007Names' "User Bob"
        assert log_results.endswith("007Names (User Bob)\n")

if __name__ == "__main__":
    if os.path.exists("tests/test_data/vault.json"):
        os.remove("tests/test_data/vault.json")
    app_process = start_app()
    drive_with_pyautogui()
    # Optionally, wait for the application process to finish
    app_process.wait()
    # Capture and print the output from the application
    capture_output(app_process)