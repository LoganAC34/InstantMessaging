import webbrowser

import wx.html

from scripts import GlobalVars
from wxglade import AboutWindow

# https://docs.wxpython.org/richtextctrl_overview.html
class AboutWindowEx(AboutWindow):
    def __init__(self, *args, **kwds):
        AboutWindow.__init__(self, *args, **kwds)
        self.SetTitle(f"About {GlobalVars.APP_NAME}")

        # Set app logo
        logo_app = wx.Bitmap.ConvertToImage(wx.Bitmap(GlobalVars.program_image))
        logo_app = logo_app.Scale(self.logo_app.Size.width, self.logo_app.Size.height, wx.IMAGE_QUALITY_HIGH)
        self.logo_app.SetBitmap(wx.Bitmap(logo_app))

        # Set publisher logo
        logo_publisher = wx.Bitmap.ConvertToImage(wx.Bitmap(GlobalVars.company_logo))
        logo_publisher = logo_publisher.Scale(self.logo_publisher.Size.width, self.logo_publisher.Size.height,
                                              wx.IMAGE_QUALITY_HIGH)
        self.logo_publisher.SetBitmap(wx.Bitmap(logo_publisher))

        # Set richTextCtrl text and size
        self.set_richtextctrl_text()
        size = (280, 200)
        self.main_text.SetSize(size)
        self.main_text.SetMinSize(size)
        self.SetSize(self.sizer_1.ComputeFittingWindowSize(self))

    def set_window_colors(self):
        #EditColorsWindowEx.preset_color_themes[]
        pass

    def set_richtextctrl_text(self):
        self.main_text.BeginTextColour(self.main_text.GetForegroundColour())

        # Title
        self.main_text.BeginBold()
        self.main_text.BeginFontSize(10)
        self.main_text.WriteText(f"{GlobalVars.APP_NAME} {GlobalVars.VERSION}")
        self.main_text.EndFontSize()
        self.main_text.EndBold()
        self.main_text.Newline()

        self.main_text.WriteText(f"Built on {GlobalVars.BUILD_DATE}")
        self.main_text.Newline()
        self.main_text.Newline()

        # Build info
        self.main_text.WriteText(f"Runtime version: Python {GlobalVars.PYTHON_BUILD_VERSION} (Packaged with PyInstaller)")
        self.main_text.Newline()

        self.main_text.WriteText(f"VM: Python {GlobalVars.PYTHON_BUILD_VERSION} (Embedded)")
        self.main_text.Newline()

        self.main_text.WriteText(f"Powered by open-source software")
        self.main_text.Newline()
        self.main_text.Newline()

        # Author Info
        self.main_text.WriteText(f"Developed by: {GlobalVars.PUBLISHER}")
        self.main_text.Newline()

        self.main_text.WriteText(f"Source code available on ")
        self.main_text.BeginTextColour((107, 155, 250))
        self.main_text.BeginUnderline()
        self.main_text.BeginURL(GlobalVars.GITHUB_REPO_LINK)
        self.main_text.WriteText("GitHub")
        self.main_text.EndURL()
        self.main_text.EndTextColour()
        self.main_text.EndUnderline()
        self.main_text.Newline()

        self.main_text.WriteText("Copyright: " + u"\u00A9" + f" 2024 {GlobalVars.AUTHOR}")
        self.main_text.Newline()

        self.main_text.WriteText(f"Licensed under the MIT License")

    def on_url_click(self, event):
        webbrowser.open(event.GetString())

    def on_close(self, event=None):
        self.Parent.Enable()
        self.Destroy()
        print("Closing about")
