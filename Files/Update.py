import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import time

from win10toast import ToastNotifier


def run(downloaded_path, current_path, new_path, pickle_file, new_sha):
    time.sleep(3)  # Wait for main app to close

    print("Remove: " + current_path)
    os.remove(current_path)  # Delete old file
    print("Move from: " + downloaded_path)
    print("Move to: " + new_path)
    shutil.move(downloaded_path, new_path)  # Move new one from temp folder
    subprocess.call('ie4uinit.exe -show', shell=True)  # Refresh icons

    print("Pickle file: " + pickle_file)
    print("New sha:" + new_sha)
    # Save current sha value:
    with open(pickle_file, 'wb') as f:
        pickle.dump(new_sha, f)

    print("Run: " + new_path)
    subprocess.Popen([new_path], start_new_session=True)
    sys.exit(0)
    #time.sleep(30)


r"""
if __name__ == '__main__':
    downloaded_path = r"C:\Users\lcarrozza\AppData\Local\Temp\Local_Instant_Messenger.exe"
    current_path = r"C:\Users\lcarrozza\Downloads\Local_Instant_Messenger.exe"
    new_path = r"C:\Users\lcarrozza\Downloads\Local_Instant_Messenger.exe"
    pickle_file = r"C:\Users\lcarrozza\AppData\Roaming\Local_Instant_Messenger\sha.pkl"
    new_sha = "12312541y3o5hb1i4u12g3ob51ou2p3hp1ui"
else:
    downloaded_path = sys.argv[1]
    current_path = sys.argv[2]
    new_path = sys.argv[3]
    pickle_file = sys.argv[4]
    new_sha = sys.argv[5]
"""
downloaded_path = sys.argv[1]
current_path = sys.argv[2]
new_path = sys.argv[3]
pickle_file = sys.argv[4]
new_sha = sys.argv[5]
run(downloaded_path, current_path, new_path, pickle_file, new_sha)