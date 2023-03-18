import os
import pickle
import shutil
import subprocess
import sys
import time


def run(downloaded_path, current_path, new_path, pkl_sha, new_sha, pkl_update):
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

                print("Pickle file: " + pkl_sha)
                print("New sha:" + new_sha)
                # Save current sha value:
                with open(pkl_sha, 'wb') as f:
                    pickle.dump(new_sha, f)

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


r"""
if __name__ == '__main__':
    downloaded_path = r"C:\Users\lcarrozza\AppData\Local\Temp\Local_Instant_Messenger.exe"
    current_path = r"C:\Users\lcarrozza\Downloads\Local_Instant_Messenger.exe"
    new_path = r"C:\Users\lcarrozza\Downloads\Local_Instant_Messenger.exe"
    pkl_sha = r"C:\Users\lcarrozza\AppData\Roaming\Local_Instant_Messenger\sha.pkl"
    new_sha = "12312541y3o5hb1i4u12g3ob51ou2p3hp1ui"
else:
    downloaded_path = sys.argv[1]
    current_path = sys.argv[2]
    new_path = sys.argv[3]
    pkl_sha = sys.argv[4]
    new_sha = sys.argv[5]
"""
downloaded_path = sys.argv[1]
current_path = sys.argv[2]
new_path = sys.argv[3]
pkl_sha = sys.argv[4]
new_sha = sys.argv[5]
pkl_update = sys.argv[6]
run(downloaded_path, current_path, new_path, pkl_sha, new_sha, pkl_update)
# sys.exit(0)
