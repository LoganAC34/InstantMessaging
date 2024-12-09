#!/usr/src/env python3
# -*- coding: UTF-8 -*-
import winreg

import psutil

from wxglade_overrides.ChatWindow import *
from wxglade_overrides.FrameSettings import *


def is_program_running():
    # Function to check if the program is already running
    if not os.path.exists(GlobalVars.lockfile):
        return False

    # Read PID from lock file
    with open(GlobalVars.lockfile, "r") as f:
        pid = f.read().strip()

    # Check if process with PID exists
    return int(pid) in (p.pid for p in psutil.process_iter())


def install_edge_browser():
    registry_keys = ['SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
                     'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}']
    for key in registry_keys:
        try:
            # noinspection LongLine
            regkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE if 'WOW6432Node' in key else winreg.HKEY_CURRENT_USER,
                                    key)
            with regkey as regkey:
                value, _ = winreg.QueryValueEx(regkey, 'pv')
                if value and value != '0.0.0.0':
                    print("Edge WebView2 is already installed. Checking for update...")
                    try:
                        subprocess.run("winget upgrade Microsoft.EdgeWebView2Runtime --accept-source-agreements "
                                       "--accept-package-agreements", check=True, shell=True)
                    except subprocess.CalledProcessError:
                        pass
                    return
        except FileNotFoundError:
            pass

    try:
        print("Installing edge browser...")
        subprocess.run(f'"{GlobalVars.edge_webview_installer}" /silent /install', check=True)
        print("Installed successfully.")
    except FileNotFoundError:
        print("Edge WebView2 installer not found.")
    except subprocess.CalledProcessError as e:
        print("Failed to install Edge WebView2:", e)


class MyApp(wx.App):
    def __init__(self):
        super().__init__(False, None, False, True)
        self.ChatWindow = None


    def OnInit(self):
        try:
            if is_program_running():
                print("Another instance of the program is already running.")
                return False

            # Write current PID to lock file
            with open(GlobalVars.lockfile, "w") as f:
                f.write(str(os.getpid()))

            # install_edge_browser() # Not needed?

            self.ChatWindow = MyFrame(None, wx.ID_ANY, "")
            self.SetTopWindow(self.ChatWindow)
            self.ChatWindow.Show()
            return True
        except Exception as e:
            print("An error occurred during initialization:", e)
            return False

    def OnExit(self):
        # Remove the lock file
        if os.path.exists(GlobalVars.lockfile):
            os.remove(GlobalVars.lockfile)

        self.Destroy()
        return 0

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
