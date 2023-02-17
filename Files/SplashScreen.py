import queue
import wx
from wx.adv import SplashScreen as SplashScreen


# class MySplashScreen
# class MyApp

# ---------------------------------------------------------------------------

class MySplashScreen(SplashScreen):
    # Create a splash screen widget.
    def __init__(self, parent=None):
        # ------------

        # This is a recipe to the screen.
        # Modify the following variables as necessary.
        bitmap = wx.Bitmap(
            name=r"C:\Users\lcarrozza\PycharmProjects\LocalInstantMessenger\Files\vector-chat-icon-png_302635.png",
            type=wx.BITMAP_TYPE_PNG)
        splash = wx.adv.SPLASH_CENTRE_ON_SCREEN
        duration = 0  # milliseconds

        # Call the constructor with the above arguments
        # in exactly the following order.
        super(MySplashScreen, self).__init__(bitmap=bitmap,
                                             splashStyle=splash,
                                             milliseconds=duration,
                                             parent=None,
                                             id=-1,
                                             style=wx.STAY_ON_TOP | wx.BORDER_NONE)

        self.Bind(wx.EVT_CLOSE, self.OnExit)

    # -----------------------------------------------------------------------

    def OnExit(self, event):
        # The program will freeze without this line.
        event.Skip()  # Make sure the default handler runs too...
        self.Destroy()
        self.Close()
        del self

        # ------------


# ---------------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):
        # ------------

        MySplash = MySplashScreen()
        MySplash.CenterOnScreen()
        MySplash.Show()
        while True:
            try:
                results = a.get(block=False, timeout=0.2)
                if results:
                    MySplash.Destroy()
                    MySplash.Close()
                    del MySplash
                    return True
            except:
                pass


# ---------------------------------------------------------------------------

def main(q, null=None):
    global a
    a = q
    app = MyApp()
    app.MainLoop()
    app.Destroy()
    del app


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    q = queue.Queue()
    main(q)
