import yaml

from Project.bin.Scripts.Global import GlobalVars
from Project.bin.wxglade.EasterEgg import *


class EasterEggOverride(EasterEgg):
    def __init__(self, *args, **kwds):
        EasterEgg.__init__(self, *args, **kwds)

        # Load the JSON file containing the game data
        yaml_file = GlobalVars.exe + r'Resources\EasterEgg.yaml'
        with open(yaml_file) as f:
            self.hints_and_answers = yaml.safe_load(f)['hints']

        self.typing_text = ''
        self.current_text = ''
        self.timer_typing = wx.Timer(self)

        # Output first hint
        # self.Output.AppendText(self.hints_and_answers[0]['hint'])
        self.TypeString(self.hints_and_answers[0]['hint'])

        self.Bind(wx.EVT_TIMER, self.typing, self.timer_typing)
        self.Input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def Processing(self, answer):
        for i, hint in enumerate(self.hints_and_answers):
            if any(answer.lower() == item.lower() for item in hint['answers']):
                hint = '\n\n' + self.hints_and_answers[i + 1]['hint']  # Get next hint
                self.TypeString(hint)
                break

    def OnKeyDown(self, event):
        # print("OnKeyDown")
        unicodeKey = event.GetUnicodeKey()
        keycode = event.KeyCode
        print(keycode)
        message = self.Input.GetValue()

        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            # Adding carriage return
            # print("Shift + Enter")
            event.Skip()
        elif unicodeKey == wx.WXK_RETURN and len(message) > 0:
            # Hitting enter with message content
            # print("Just Enter with message")
            # self.TypeString('\n\nYou: ' + message)
            self.Processing(message)
            self.Input.Clear()
        elif unicodeKey == wx.WXK_RETURN and len(message) == 0:
            # Prevents sending blank message when hitting enter twice.
            # print("Just Enter")
            pass
        elif keycode in GlobalVars.allowed_keys:
            # print("Allowable character")
            # Allowing various function keys (Arrow keys, Home, End, Page up/down)
            event.Skip()
        else:
            event.Skip()

    def OnResize(self, event):
        self.Output.Layout()
        self.Output.SetScrollPos(orientation=wx.VERTICAL, pos=self.Output.GetScrollRange(wx.VERTICAL))
        self.Output.SetInsertionPoint(-1)
        if event:
            event.Skip()

    def on_close(self, event):
        self.Destroy()

    def TypeString(self, text):
        if text not in self.Output.GetLabel():
            typing_speed = round(2000 / len(text))  # Time in milliseconds it should take to type the entire message.
            self.typing_text += text
            self.timer_typing.Start(typing_speed)
            self.Input.Disable()
        # event.Skip()

    def typing(self, event):
        self.current_text += self.typing_text[len(self.current_text)]
        self.Output.SetLabelText(self.current_text)
        wx.CallAfter(self.OnResize, None)
        if self.current_text == self.typing_text:
            self.timer_typing.Stop()
            self.Input.Enable()
