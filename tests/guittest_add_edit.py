import os
import time
import subprocess
import pyautogui as gui

# Test Script to exercise Add and Edit dialogs, including Lookup

def start_app():
    root = os.getcwd()
    # There's a special config file for this test that has a temp vault location
    arg1 = root + os.path.normpath("/tests/test_data/config_test1.ini")
    # Determine the command based on the platform
    if os.name == 'nt':  # Windows
        venv_path = os.path.join(root, 'venv', 'Scripts', 'python.exe')
        command = [venv_path, 'src\\main.py', '-c', arg1]
    else:  # Unix-based systems (Linux, macOS)
        command = ['python3', 'src/main.py', '-c', arg1]
    
    # Start EasyAuth with a custom config file that points to a test directory for the vault
    process = subprocess.Popen(command,
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
    gui.hotkey('alt','s')                   # Search box
    gui.typewrite("W")                    # Find Woogle
    gui.press(['tab','space'])              # Tab to edit button, Open edit dialog
    gui.press('tab')                        # tab to user field
    gui.typewrite('User Bob')               # update user
    gui.hotkey('alt','s')                   # save & close

    gui.hotkey('alt','s')                   # Search box
    # 'W' will still be in search box
    gui.press(['tab','space'])              # Tab to edit button, Open edit dialog
    gui.hotkey('alt', 'l')                  # Open Lookup
    gui.typewrite('spring')                 # Enter name in search field
    gui.press('enter')                      # Accept
    gui.hotkey('alt', 'l')                  # Open Lookup
    gui.press(['down','down'])              # Browse the list
    gui.press('enter')                      # Accept
    gui.hotkey('alt','s')                   # save & close
    time.sleep(0.5)
    # NB: after update to 007Names the display is blank because the search box still retains 'W'
    # and 007 doesn't match 'W'
    gui.hotkey('alt','s')                   # search box
    gui.press('backspace')                  # delete 'W' and 007appears.


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
    from pathlib import Path
    # For this test we make a vault in developer's home directory
    vault = os.path.join(Path.home(),os.path.normpath("vault.json"))
    if os.path.exists(vault):
        # Remove any prior artifacts
        os.remove(vault)
    app_process = start_app()
    drive_with_pyautogui()
    # Optionally, wait for the application process to finish
    app_process.wait()
    # Capture and print the output from the application
    capture_output(app_process)
    # Remove the temporary vault
    if os.path.exists(vault):
        os.remove(vault)
        vaultbak = os.path.join(Path.home(),os.path.normpath("vault.backup.json"))
        os.remove(vaultbak)
