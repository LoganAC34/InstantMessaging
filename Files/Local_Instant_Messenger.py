import _thread
import os
import pathlib
import pickle
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib
from os.path import exists
from threading import Thread
from urllib.request import urlopen

import requests
import wx
import wx.adv
import wx.lib.agw.persist
import wx.lib.scrolledpanel

# Relative and exe paths
try:
    # we are running in a bundle
    exe = sys._MEIPASS + '\\'
    relative = os.path.dirname(sys.executable) + '\\'
except AttributeError:
    # we are running in a normal Python environment
    exe = os.path.dirname(os.path.abspath(__file__)) + '\\'
    relative = '\\'.join(exe.split('\\')[:-2]) + '\\'

# Get exe location
if getattr(sys, 'frozen', False):
    app_path = sys.executable
else:
    app_path = os.path.abspath(__file__)

chatHistory = []
Logan_PC = 'CADD-13'
Tyler_PC = 'CADD-4'
if socket.gethostname() == Logan_PC:
    send_host_name = 'Logan'
    receiving_host_name = 'Tyler'
else:
    send_host_name = 'Tyler'
    receiving_host_name = 'Logan'
u_separator = '?>:'
icon = exe + 'Local_Instant_Messenger.ico'

my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / "Local_Instant_Messenger"
try:
    my_data_dir.mkdir(parents=True)
except FileExistsError:
    pass

pkl_sha = my_data_dir / 'sha.pkl'
pkl_update = my_data_dir / 'update.pkl'

global worker

"""
# Event handlers (first three go in main script)
EVT_RECEIVE_MSG_ID = wx.ID_ANY  # Define notification event for thread completion
worker = None  # And indicate we don't have a worker thread yet


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


EVT_RECEIVE_MSG(self, self.ReceiveMsg) # Set up event handler for any worker thread results (Goes in __init__ function)

# (Goes in GUI to define outside function
def OnStart(self):
    # Start Computation.
    # Trigger the worker thread unless it's already busy
    if not worker:
        # self.status.SetLabel('Starting computation')
        worker = SocketWorkerThread(self)

wx.PostEvent(self._notify_window, ReceiveMessage(msg)) # Goes in GUI function to trigger outside function

self._notify_window = notify_window # Goes in outside function to carry data
"""

# Receive message event ---------------------------------------------
EVT_RECEIVE_MSG_ID = wx.ID_ANY  # Define notification event for thread completion
ID_TRIGGER_FUNC = wx.ID_ANY


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
class SocketWorkerThread(Thread):
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
        host = socket.gethostname()
        server_ip = socket.gethostbyname(host)
        receive_port = 3434
        if host == Logan_PC:
            send_host = Tyler_PC
            send_port = 3434
        else:
            send_host = Logan_PC
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
class LogPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)

        # box = wx.StaticBox(self, label="", size=wx.Size(1000, 1000))
        # self.sizer_log = wx.StaticBoxSizer(wx.VERTICAL, self)
        self.SetupScrolling(self, scrollToTop=False)
        # self.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))

        # Font Height
        font = wx.Font()
        self.dc = wx.ScreenDC()
        self.dc.SetFont(font)
        self.single_height = self.dc.GetMultiLineTextExtent('')

        # Chat log
        self.chat_box = wx.StaticText(self, style=wx.TE_MULTILINE | wx.ST_NO_AUTORESIZE)
        self.chat_box.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        self.chat_box.SetForegroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))
        self.chat_box.SetFont(font)
        # self.sizer_log.Add(self.chat_box, 1, wx.ALL | wx.EXPAND, 0)

        # Sizer
        self.main_sizer = wx.BoxSizer()
        # self.main_sizer.Add(self.sizer_log, 1, wx.EXPAND)
        self.main_sizer.Add(self.chat_box, 1, wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def append_chat(self, msg):
        if u_separator in msg:
            contents = msg.split(u_separator)
            u = contents[0]
            msg = contents[1]
            if not app.IsActive():
                popup = wx.adv.NotificationMessage(title=u, message=msg)
                popup.SetIcon(wx.Icon(icon))
                popup.Show()
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
        size = self.dc.GetMultiLineTextExtent(chatHistory_Display)
        size.Height = size.Height - self.single_height.Height * 2
        self.chat_box.SetMinSize(size)
        self.Layout()
        self.SetupScrolling(scrollToTop=False)
        self.Scroll(0, size.Height)


class SendPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Get parent
        grand_parent = parent.GetParent()
        self.function = grand_parent.sub_panel_Log

        # Send button
        self.my_btn = wx.Button(self, label='Send')
        self.my_btn.Bind(wx.EVT_BUTTON, self.send_message)  # Even bind

        # Message box
        self.text_ctrl = wx.TextCtrl(style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, parent=self)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.key_code)

        # sizer
        box_send = wx.BoxSizer()
        box_send.Add(self.my_btn, 0, wx.ALL, 5)
        box_send.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box_send)

    def send_message(self):
        msg = self.text_ctrl.GetValue()
        if msg:
            self.function.append_chat(msg)
            self.text_ctrl.Clear()
            worker.send_message(send_host_name + u_separator + msg)

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


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f'Chatting with {receiving_host_name}', name='Local Instant Messenger')

        # Remember window size and position
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._persistMgr = wx.lib.agw.persist.PersistenceManager.Get()
        _configFile = my_data_dir / 'persist-saved-cfg'
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print("No config file")

        # Panels
        main_panel = wx.Panel(self)
        self.sub_panel_Log = LogPanel(main_panel)
        self.sub_panel_Send = SendPanel(main_panel)

        self.SetIcon(wx.Icon(icon))  # App icon
        #self.Update = False
        # Set Update variable to false
        with open(pkl_update, 'wb') as f:
            pickle.dump(False, f)

        # Set up event handler for any worker thread results
        global worker
        worker = None  # And indicate we don't have a worker thread yet

        # Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.sub_panel_Log, 1, wx.EXPAND, 5)
        main_sizer.Add(self.sub_panel_Send, 0, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)
        self.OnStart()  # Start chat server
        self.SetMinSize(wx.Size(300, 300))

        # Bind
        EVT_RECEIVE_MSG(self, self.ReceiveMsg)  # Set event for receive message

    def OnStart(self):
        # Start Computation.
        # Trigger the worker thread unless it's already busy
        global worker
        if not worker:
            # self.status.SetLabel('Starting computation')
            worker = SocketWorkerThread(self)
        self.CheckForUpdate()

    def ReceiveMsg(self, event):
        self.sub_panel_Log.append_chat(event.data)

    def OnClose(self, event):
        self._persistMgr.SaveAndUnregister()
        worker.abort()

        # Get Update variable
        if exists(pkl_update):
            with open(pkl_update, 'rb') as f:
                Update = pickle.load(f)
        else:
            Update = False
            print("No local sha value")

        if Update:
            # Copy Update script to temp folder
            py_update = 'Update.exe'
            src_script_path = exe + py_update
            dst_script_path = os.path.join(tempfile.gettempdir(), py_update)
            print("Source: " + src_script_path)
            print("Paste: " + dst_script_path)
            shutil.copy(src_script_path, dst_script_path)

            # Copy Notification icon to temp folder
            src_icon_path = icon
            dst_icon_path = os.path.join(tempfile.gettempdir(), os.path.basename(icon))
            print("Source: " + src_icon_path)
            print("Paste: " + dst_icon_path)
            shutil.copy(src_icon_path, dst_icon_path)

            # Update script
            update_script = os.path.join(tempfile.gettempdir(), py_update)
            subprocess.Popen([update_script,
                              self.temp_file,
                              app_path, app_path,
                              pkl_sha, self.sha_github,
                              pkl_update],
                             start_new_session=True
                             )
            sys.exit(0)

        event.Skip()

    def CheckForUpdate(self):
        try:
            # Get GitHub sha value:
            url_sha = 'https://api.github.com/repos/LoganAC34/InstantMessaging/contents/Local_Instant_Messenger.exe'
            sha_github = requests.get(url_sha).json()
            self.sha_github = sha_github['sha']

            # Get local file sha value:
            if exists(pkl_sha):
                with open(pkl_sha, 'rb') as f:
                    sha_local = pickle.load(f)
            else:
                sha_local = "None"
                print("No local sha value")

            print("Github sha: " + self.sha_github)
            print("Local sha: " + sha_local)

            if self.sha_github != sha_local:
                #self.Update = True
                # Set Update variable to True
                with open(pkl_update, 'wb') as f:
                    pickle.dump(False, f)

                # Download GitHub file
                url_download = 'https://raw.githubusercontent.com/LoganAC34/' \
                               'InstantMessaging/master/Local_Instant_Messenger.exe'
                self.temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(url_download))
                print(self.temp_file)

                # Download file
                t = Thread(target=self.DownloadUpdate, args=[url_download, self.temp_file])
                t.start()

            else:
                print("Program is up to date!")

        except Exception as e:
            print(e)
            pass

    @staticmethod
    def DownloadUpdate(url_download, temp_file):
        print("Downloading updated file...")
        # Notification about update
        update_popup = wx.adv.NotificationMessage(title='Downloading update...',
                                                  message="There is an update available. Please wait for it to finish "
                                                          "downloading before closing the program")
        update_popup.SetIcon(wx.Icon(icon))
        update_popup.Show()

        # Download current file
        while True:
            try:
                urllib.request.urlretrieve(url_download, filename=temp_file)
                break
            except Exception as e:
                print("Download failed. Trying again.")
                print(e)
                pass

        # Notification about update
        update_popup = wx.adv.NotificationMessage(title='Update Available',
                                                  message="There is an update available. Close and restart "
                                                          "program to use updated program.")
        update_popup.SetIcon(wx.Icon(icon))
        update_popup.Show()

        print("Done.")

    @staticmethod
    def UpdateNow(downloaded_path, current_path, new_path, pkl_sha, new_sha, pkl_update):
        print("Running update file")
        sys.path.insert(0, tempfile.gettempdir())
        import Update
        Update.run(downloaded_path, current_path, new_path, pkl_sha, new_sha, pkl_update)


if __name__ == '__main__':
    app = wx.App()
    app.SetAppName('Local Chat')
    app.SetVendorName('Logan')
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
