#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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


# end of class MyApp

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
