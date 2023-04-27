from Project.bin.Scripts.Global import GlobalVars
from Project.bin.wxglade.EasterEggWindow import *


class EasterEgg(EasterEggWindow):
    def __init__(self, *args, **kwds):
        EasterEggWindow.__init__(self, *args, **kwds)

        self.hints_and_answers = [
            ("A million deaths is not enough for Master Rahool.",
             "01000001 00100000 01101101 01101001 01101100 01101100 01101001 "
             "01101111 01101110 00100000 01100100 01100101 01100001 01110100 "
             "01101000 01110011 00100000 01101001 01110011 00100000 01101110 "
             "01101111 01110100 00100000 01100101 01101110 01101111 01110101 "
             "01100111 01101000 00100000 01100110 01101111 01110010 00100000 "
             "01001101 01100001 01110011 01110100 01100101 01110010 00100000 "
             "01010010 01100001 01101000 01101111 01101111 01101100 00101110"),
            ("Test", "Testing")
        ]
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown, self)

    def Processing(self):
        pass

    def OnKeyDown(self, event):
        print("OnKeyDown")
        # print('Onkey')
        unicodeKey = event.GetUnicodeKey()
        keycode = event.KeyCode
        message = self.GetValue()

        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            # Adding carriage return
            print("Shift + Enter")
            event.Skip()
        elif unicodeKey == wx.WXK_RETURN and len(message) > 0:
            # Hitting enter with message content
            print("Just Enter with message")
        elif unicodeKey == wx.WXK_RETURN and len(message) == 0:
            # Prevents sending blank message when hitting enter twice.
            print("Just Enter")
        elif keycode in GlobalVars.allowed_keys:
            # Allowing various function keys (Arrow keys, Home, End, Page up/down)
            event.Skip()
