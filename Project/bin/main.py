#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from wxglade_overrides.ChatWindow import *
from wxglade_overrides.FrameSettings import *


class MyApp(wx.App):
    def __init__(self):
        super().__init__(False, None, False, True)
        self.ChatWindow = None

    def OnInit(self):
        self.ChatWindow = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.ChatWindow)
        self.ChatWindow.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
