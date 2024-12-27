from wxglade import ErrorDialogWindow


class ErrorDialogWindowEx(ErrorDialogWindow):
    def __init__(self, *args, **kwds):
        ErrorDialogWindow.__init__(self, *args, **kwds)

    def OnClose(self, event):
        self.Parent.Enable()
        self.Destroy()
        event.Skip()
