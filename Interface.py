import _thread
import socket
import time
from threading import Thread

import wx
import os
import wx.lib.agw.persist as PM

# from Server import WorkerThread

chatHistory = []
connections = []
user = "Logan"
name = 'Tyler'
u_separator = '?>:'
client_keyword = 'Client-+:'
clients = ['CADD-13', 'CADD-4']

# Receive message event ---------------------------------------------
EVT_RECEIVE_MSG_ID = wx.ID_ANY  # Define notification event for thread completion


def EVT_RECEIVE_MSG(win, func):
    # Define Result Event.
    win.Connect(-1, -1, EVT_RECEIVE_MSG_ID, func)


class ReceiveMessage(wx.PyEvent):
    # Simple event to carry arbitrary result data.
    def __init__(self, data):
        # Init Result Event.
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RECEIVE_MSG_ID)
        self.data = data


# Receive connection event ---------------------------------------------
EVT_RECEIVE_CON_ID = wx.ID_ANY  # Define notification event for thread completion


def EVT_RECEIVE_CON(win, func):
    # Define Result Event.
    win.Connect(-1, -1, EVT_RECEIVE_CON_ID, func)


class ReceiveConnection(wx.PyEvent):
    # Simple event to carry arbitrary result data.
    def __init__(self, data):
        # Init Result Event.
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RECEIVE_CON_ID)
        self.data = data


# SERVER ----------------------------------------------------------------------------------------
class WorkerThread(Thread):
    """Worker Thread Class."""
    print("Server Started")

    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._msg = ""
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        server = 'CADD-13'
        host = socket.gethostname()
        server_ip = socket.gethostbyname(server)
        port = 3434
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if host == server:
            try:
                server = client
                server.bind((server_ip, port))
                server.listen(5)
            except:
                print("Bind failed")
            else:
                print("Bind successful: " + server_ip)
                clientsocket = None
                while True:
                    if clientsocket is None:
                        print("[Waiting for connection..]")
                        (clientsocket, address) = server.accept()
                        print("Client accepted from", address[0])
                        clientsocket.settimeout(0.1)
                        clientsocket.sendto("Logan".encode("UTF-8"), address)
                        clientsocket.settimeout(0.1)
                        username, address = clientsocket.recvfrom(1024)
                        username = username.decode("UTF-8")
                        wx.PostEvent(self._notify_window, ReceiveConnection(str(address[0]) + '=' + username))
                    else:
                        # print("[Waiting for response...]")
                        rev_msg, address = clientsocket.recvfrom(1024)
                        if rev_msg:
                            msg = rev_msg.decode("UTF-8")
                            print(rev_msg)
                            wx.PostEvent(self._notify_window, ReceiveMessage(rev_msg))  # Post even for GUI to react
                        if self._msg:
                            clientsocket.sendto(self._msg.encode("UTF-8"), address)
                            print(self._msg)
                    """
                    if self._msg:
                        # Use a result of None to acknowledge the send_message (of
                        # course you can use whatever you'd like or even
                        # a separate event type)
                        wx.PostEvent(self._notify_window, ReceiveMessage(None))
                        return
                    """
        else:
            client.connect((server_ip, port))
            username, address = client.recvfrom(1024)
            username = username.decode("UTF-8")
            wx.PostEvent(self._notify_window, ReceiveConnection(server_ip + '=' + username))
            client.sendto("Tyler".encode("UTF-8"), (server_ip, port))

    def send_message(self, msg):
        # send_message worker thread.
        # Method for use by main thread to signal a send_message
        self._msg = msg



# GUI --------------------------------------------------------------------------------------
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f'Chatting with {name}')

        # Remember window size and position
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._persistMgr = PM.PersistenceManager.Get()
        _configFile = os.path.join(os.getcwd(), "persist-saved-cfg")  # getname()
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print(" no work ")

        panel = wx.Panel(self)

        # Set up event handler for any worker thread results
        EVT_RECEIVE_MSG(self, self.ReceiveMsg)
        EVT_RECEIVE_CON(self, self.ReceiveCon)
        self.worker = None  # And indicate we don't have a worker thread yet

        # Chat log
        self.chat_box = wx.StaticText(panel, style=wx.TE_MULTILINE | wx.BORDER_THEME | wx.VSCROLL | wx.ST_NO_AUTORESIZE)
        self.chat_box.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        self.chat_box.SetForegroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))

        # Send button
        self.my_btn = wx.Button(panel, label='Send')
        self.my_btn.Bind(wx.EVT_BUTTON, self.send_message)  # Even bind

        # Message box
        self.text_ctrl = wx.TextCtrl(style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, parent=panel)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.key_code)  # wx.EVT_TEXT_ENTER | wx.EVT_KEY_DOWN

        # Add to boxes and sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        box_send = wx.BoxSizer(wx.HORIZONTAL)
        box_send.Add(self.my_btn, 0, wx.ALL, 5)
        box_send.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.chat_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(box_send, 0, wx.EXPAND | wx.ALL, 5)  # Add send sizer to main

        panel.SetSizer(sizer)
        self.OnStart(None)  # Start chat server
        self.Show()

    def OnStart(self, event):
        # Start Computation.
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            # self.status.SetLabel('Starting computation')
            self.worker = WorkerThread(self)

    def ReceiveMsg(self, event):
        # Show Result status.
        if event.data:
            self.append_chat(event.data)
        # In either event, the worker is done
        # self.worker = None

    global addresses
    addresses = {}

    def ReceiveCon(self, event):
        # Show Result status.
        data = event.data
        data = data.split('=')
        username = data[0]
        address = data[1]
        # if address not in addresses:
        addresses[address] = username

    def append_chat(self, msg):
        if u_separator in msg:
            u = msg.split(u_separator)[0]
            msg = msg.replace(u + u_separator, '')
        else:
            u = user
        u += ':'
        msg_padded = msg.replace('\n', '\n' + 16 * ' ')
        msg = f'{u:<{10}}{msg_padded}'
        chatHistory.append(msg)
        chatHistory_Display = ''
        for message in chatHistory:
            chatHistory_Display += message + '\n'
        self.chat_box.SetLabel(chatHistory_Display)

    def send_message(self, event):
        msg = self.text_ctrl.GetValue()
        if msg:
            self.append_chat(msg)
            self.text_ctrl.Clear()
            self.worker.send_message(msg)
            """
            to_send = msg.encode("UTF-8")
            # clientsocket = connections[0]
            # clientsocket.send(to_send)
            
            # Send to recipient
            client = socket.socket()
            ip = socket.gethostbyname('CADD-13')
            port = 3434

            try:
                client.connect((ip, port))
            except:
                print("Not connected to client")
            else:
                print("Connect to client: ", ip)
                to_send = msg.encode("UTF-8")
                client.sendto(to_send)
            """

    def key_code(self, event):
        unicodeKey = event.GetUnicodeKey()
        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            self.text_ctrl.WriteText('\n')
            # print("Shift + Enter")
        elif unicodeKey == wx.WXK_RETURN:
            self.send_message(self)
            # print("Just Enter")
        else:
            event.Skip()
            # print("Any other character")

    def on_close(self, event):
        self._persistMgr.SaveAndUnregister()
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
