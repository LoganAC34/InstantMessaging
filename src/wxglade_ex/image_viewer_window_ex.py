import wx
from wxglade import ImageViewerWindow


class ImageViewerWindowEx(ImageViewerWindow):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((425, 324))
        self.SetTitle("frame")

        # Tool Bar
        self.ImageViewer_toolbar = wx.ToolBar(self, -1)
        self.SetToolBar(self.ImageViewer_toolbar)
        self.ImageViewer_toolbar.Realize()


        self.panel_1 = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SIMPLE)
        self.panel_1.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.Layout()
