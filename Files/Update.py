import os
import pickle
import shutil
import subprocess
import time

from wx import wx


def run(downloaded_path, current_path, new_path, pickle_file, new_sha):
    time.sleep(3)
    os.remove(current_path)  # Delete old file
    shutil.move(downloaded_path, new_path)  # Move new one from temp folder
    subprocess.call('ie4uinit.exe -show', shell=True)  # Refresh icons

    # Save current sha value:
    with open(pickle_file, 'wb') as f:
        pickle.dump(new_sha, f)

    # Notification about update
    update_popup = wx.adv.NotificationMessage(title='Update Done!',
                                              message="You can now restart the program.")
    update_popup.SetIcon(wx.Icon('vector-chat-icon-png_302635.png'))
    update_popup.Show()


if __name__ == '__main__':
    run()
