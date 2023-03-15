import _thread
import os
import socket
import subprocess
from threading import Thread

import wx
import wx.lib.agw.persist as pm

# from Server.py import SocketWorkerThread

chatHistory = []
if socket.gethostname() == 'CADD-13':
    send_host_name = 'Logan'
    receiving_host_name = 'Tyler'
else:
    send_host_name = 'Tyler'
    receiving_host_name = 'Logan'
u_separator = '?>:'

# Receive message event ---------------------------------------------
EVT_RECEIVE_MSG_ID = wx.ID_ANY  # Define notification event for thread completion
ID_STOP = wx.ID_ANY


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


# SERVER ----------------------------------------------------------------------------------------
class WorkerThread(Thread):
    """Worker Thread Class."""
    print("Server.py Started")

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
        host = socket.gethostname()
        server_ip = socket.gethostbyname(host)
        receive_port = 3434
        if host == 'CADD-13':
            send_host = 'CADD-7'
            send_port = 3434
        else:
            send_host = 'CADD-13'
            send_port = 3434

        send_host = socket.gethostbyname(send_host)
        _thread.start_new_thread(self.run_server, (server_ip, receive_port))
        self._want_abort = None
        while True:
            if self._msg:
                while True:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        print("Connecting to " + send_host + ":" + str(send_port))
                        client.settimeout(0.1)
                        client.connect((send_host, send_port))
                        client.send(self._msg.encode("UTF-8"))
                        print(self._msg)
                        self._msg = ""
                        break
                    except Exception as e:
                        print(e)
                        batchMessage = self._msg.replace(u_separator, ': ')
                        batchMessage = batchMessage.replace('\n', ' ')
                        subprocess.call(f'msg /SERVER:{send_host} * /TIME:60 "{batchMessage}"', shell=True)
                        self._msg = ""
                        break
                        #time.sleep(1)
                    #client.close()
                    #client = socket.socket()
                    #client.connect_ex((PC_Other_IP, send_port))
            if self._want_abort:
                break

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

    def run_server(self, host, port):
        """Handle all incoming connections by spawning worker threads."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        print("Bind successful: " + host)
        server.listen(5)
        while True:
            _thread.start_new_thread(self.handle_connection, server.accept())

    def handle_connection(self, client, address):
        print("Client accepted from", address)
        client.settimeout(0.1)
        msg = client.recv(1024).decode("UTF-8")
        wx.PostEvent(self._notify_window, ReceiveMessage(msg))

    def send_message(self, msg):
        # send_message worker thread.
        # Method for use by main thread to signal a send_message
        self._msg = msg
        # print("Event triggered")
        # print(self._msg)


# GUI --------------------------------------------------------------------------------------
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f'Chatting with {receiving_host_name}')

        # Remember window size and position
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._persistMgr = pm.PersistenceManager.Get()
        _configFile = os.path.join(os.getcwd(), "persist-saved-cfg")  # getname()
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print(" no work ")

        panel = wx.Panel(self)

        # Set up event handler for any worker thread results
        EVT_RECEIVE_MSG(self, self.ReceiveMsg)
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
        self.OnStart()  # Start chat server
        self.Show()

    def OnStart(self):
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

    def append_chat(self, msg):
        if u_separator in msg:
            contents = msg.split(u_separator)
            u = contents[0]
            msg = contents[1]
        else:
            u = send_host_name
        u += ':'
        msg_padded = msg.replace('\n', '\n' + 16 * ' ')
        msg = f'{u:<{10}}{msg_padded}'
        chatHistory.append(msg)
        chatHistory_Display = ''
        for message in chatHistory:
            chatHistory_Display += message + '\n'
        self.chat_box.SetLabel(chatHistory_Display)

    def send_message(self):
        msg = self.text_ctrl.GetValue()
        if msg:
            self.append_chat(msg)
            self.text_ctrl.Clear()
            self.worker.send_message(send_host_name + u_separator + msg)

    def key_code(self, event):
        unicodeKey = event.GetUnicodeKey()
        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            self.text_ctrl.WriteText('\n')
            # print("Shift + Enter")
        elif unicodeKey == wx.WXK_RETURN:
            self.send_message()
            # print("Just Enter")
        else:
            event.Skip()
            # print("Any other character")

    def on_close(self, event):
        self._persistMgr.SaveAndUnregister()
        self.worker.abort()
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
