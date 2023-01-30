import os
import pickle
import shutil
import subprocess
import sys
import time


def run(downloaded_path, current_path, new_path, pkl_sha, new_sha, pkl_update):
    time.sleep(3)  # Wait for main app to close

    print("Remove: " + current_path)
    os.remove(current_path)  # Delete old file
    print("Move from: " + downloaded_path)
    print("Move to: " + new_path)
    shutil.move(downloaded_path, new_path)  # Move new one from temp folder
    subprocess.call('ie4uinit.exe -show', shell=True)  # Refresh icons

    print("Pickle file: " + pkl_sha)
    print("New sha:" + new_sha)
    # Save current sha value:
    with open(pkl_sha, 'wb') as f:
        pickle.dump(new_sha, f)

    # Update variable
    with open(pkl_update, 'wb') as f:
        pickle.dump(False, f)

    print("Run: " + new_path)
    subprocess.Popen([new_path], start_new_session=True)
    sys.exit(0)

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
