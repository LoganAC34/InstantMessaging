import os
import pickle
import shutil
import subprocess
import sys
import time


def run(downloaded_path, current_path, new_path, pkl_update):
    print("Overwrite: " + current_path)
    print("Move from: " + downloaded_path)
    print("Move to: " + new_path)
    time.sleep(3)  # Give time for main program to finish closing
    timer = 0
    error = None
    while True:
        if timer < 10:  # After 10s of failing, cancel update.
            try:
                shutil.copy(downloaded_path, new_path)  # Move new one from temp folder
                os.remove(downloaded_path)
                subprocess.call('ie4uinit.exe -show', shell=True)  # Refresh icons

                # Set Update variable
                with open(pkl_update, 'wb') as f:
                    pickle.dump(False, f)

                print("Run: " + new_path)
                subprocess.Popen([new_path], start_new_session=True)
                time.sleep(3)  # Gives time to see CMD prompt when debugging.
                break

            except PermissionError as e:
                error = e
                time.sleep(0.1)
                timer += 0.1
        else:
            raise error


run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# sys.exit(0)
