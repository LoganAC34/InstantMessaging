import os
import pickle
import shutil
import subprocess


def run(downloaded_path, current_path, new_path, pickle_file, new_sha):
    os.remove(current_path)  # Delete old file
    shutil.move(downloaded_path, new_path)  # Move new one from temp folder
    subprocess.call('ie4uinit.exe -show', shell=True)  # Refresh icons

    # Save current sha value:
    with open(pickle_file, 'wb') as f:
        pickle.dump(new_sha, f)
