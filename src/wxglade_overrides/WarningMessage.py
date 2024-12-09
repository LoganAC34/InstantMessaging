from wxglade.ErrorDialog import *


class WaringMessage(ErrorDialog):
    def __init__(self, *args, **kwds):
        ErrorDialog.__init__(self, *args, **kwds)

    def OnClose(self, event):
        self.Parent.Enable()
        self.Destroy()
        event.Skip()
