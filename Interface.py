import wx, os
import wx.lib.agw.persist as PM

chatHistory = []


class MyFrame(wx.Frame):
    def __init__(self):
        name = 'Logan'
        super().__init__(parent=None, title=f'Chatting with {name}')

        # Remember window size and position
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._persistMgr = PM.PersistenceManager.Get()
        _configFile = os.path.join(os.getcwd(), "persist-saved-cfg")  # getname()
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print(" no worky  ")

        panel = wx.Panel(self)

        # Chat log
        self.chat_box = wx.StaticText(panel, style=wx.TE_MULTILINE | wx.BORDER_THEME | wx.VSCROLL | wx.ST_NO_AUTORESIZE)
        self.chat_box.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        self.chat_box.SetForegroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))

        # Send button
        self.my_btn = wx.Button(panel, label='Send')
        self.my_btn.Bind(wx.EVT_BUTTON, self.send_message)  # Even bind

        # Message box
        self.text_ctrl = wx.TextCtrl(style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, parent=panel)
        self.text_ctrl.Bind(wx.EVT_TEXT_ENTER, self.key_code)

        # Add to boxes and sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        box_send = wx.BoxSizer(wx.HORIZONTAL)
        box_send.Add(self.my_btn, 0, wx.ALL, 5)
        box_send.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.chat_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(box_send, 0, wx.EXPAND | wx.ALL, 5)  # Add send sizer to main

        panel.SetSizer(sizer)
        self.Show()

    def append_chat(self, msg):
        chatHistory.append(msg)
        chatHistory_Display = ''
        for message in chatHistory:
            chatHistory_Display += message + '\n'
        self.chat_box.SetLabel(chatHistory_Display)

    def send_message(self, event):
        value = self.text_ctrl.GetValue()
        if value:
            print(value)
            self.append_chat(value)
            self.text_ctrl.Clear()

    def key_code(self, event):
        if wx.KeyboardState.ShiftDown:
            self.text_ctrl.WriteText('\n')
        else:
            self.send_message(self)

    def on_close(self, event):
        self._persistMgr.SaveAndUnregister()
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
