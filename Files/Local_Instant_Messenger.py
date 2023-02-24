import os
import pathlib
import pickle
import queue
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from os.path import exists
from tempfile import SpooledTemporaryFile

import requests
import wx
import wx.adv
import wx.lib.agw.persist
import wx.lib.scrolledpanel
from cryptography.fernet import Fernet
from wx.lib.expando import ExpandoTextCtrl

import GetIP
import SplashScreen

# Relative and exe paths
try:
    # we are running in a bundle
    # noinspection PyProtectedMember
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
    app_path = r"C:\Users\lcarrozza\Downloads\Local_Instant_Messenger.exe"  # os.path.abspath(__file__)

# App data folder
my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / "Local_Instant_Messenger"
try:
    my_data_dir.mkdir(parents=True)
except FileExistsError:
    pass

# Pickle variable files
pkl_sha = my_data_dir / 'sha.pkl'
pkl_update = my_data_dir / 'update.pkl'
plk_IP = my_data_dir / 'ip.pkl'

# User IPs
debug = False
splash_screen_toggle = False
if splash_screen_toggle:
    q = queue.Queue()
    splash_screen = threading.Thread(target=SplashScreen.main, args=(q, None))
    splash_screen.daemon = True
    splash_screen.start()
if debug:
    user_1 = socket.gethostbyname('CADD-13')
    user_2 = socket.gethostbyname('CADD-7')
else:
    user_1 = GetIP.user_ip('lcarrozza', plk_IP)
    user_2 = GetIP.user_ip('truby', plk_IP)

# PC IP and names
cur_IP = socket.gethostbyname(socket.gethostname())

PC_local_IP = cur_IP
if cur_IP == user_1:
    PC_Local_Name = 'Logan'
    PC_Other_Name = 'Tyler'
    PC_Other_IP = user_2
else:
    PC_Local_Name = 'Tyler'
    PC_Other_Name = 'Logan'
    PC_Other_IP = user_1

if splash_screen_toggle:
    # noinspection PyUnboundLocalVariable
    q.put(True)
    # noinspection PyUnboundLocalVariable
    splash_screen.join()
    del splash_screen

print("Local PC: " + PC_Local_Name + " - " + PC_local_IP)
print("Remote PC: " + PC_Other_Name + " - " + PC_Other_IP)

# Global Variables
chatHistory = []  # Initialize chat history
chatHistory_names = []  # Initialize chat history
loop_wait = 0.001
u_separator = '?>:'
icon = exe + 'Local_Instant_Messenger.ico'
key = b'zBfp5pkJ_-UniuIQI0dzMuf3mTIm6DRkpURXoZpA-Yo='
cipher_key = Fernet(key)

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

# Sent Method Event ---------------------------------------------
EVT_SENT_THROUGH_APP_ID = wx.ID_ANY  # Define notification event for thread completion


def EVT_SENT_THROUGH_APP(win, func):
    # Define Result Event.
    win.Connect(-1, -1, EVT_SENT_THROUGH_APP_ID, func)


class SentThroughApp(wx.PyEvent):
    # Simple event to carry arbitrary result data.
    def __init__(self, data):
        # Init Result Event.
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_SENT_THROUGH_APP_ID)
        self.data = data


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


# SERVER ----------------------------------------------------------------------------------------
class SocketWorkerThread(threading.Thread):
    """Worker Thread Class."""
    print("Server Started")

    def __init__(self, notify_window, queue_abort):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._want_abort = None
        self._queue_abort = queue_abort
        self._notify_window = notify_window
        self._msg = ""
        self.daemon = True
        self.start()

    def run(self):
        """Run Worker Thread."""
        receive_port = 3434
        send_port = 3434
        t = threading.Thread(target=self.run_server, args=(PC_local_IP, receive_port))
        t.daemon = True
        t.start()

        while True:
            if self._msg:
                while True:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        print("Connecting to " + PC_Other_IP + ":" + str(send_port))
                        client.settimeout(0.1)
                        client.connect((PC_Other_IP, send_port))
                        encrypted_msg = cipher_key.encrypt(self._msg.encode())  # Encrypt message
                        client.send(encrypted_msg)
                        print(self._msg)
                        wx.PostEvent(self._notify_window, SentThroughApp(True))
                    except Exception as e:
                        print(e)
                        batchMessage = self._msg.replace(u_separator, ': ')
                        batchMessage = batchMessage.replace('\n', ' ')
                        subprocess.call(f'msg /SERVER:{PC_Other_IP} * /TIME:60 "{batchMessage}"', shell=True)
                        wx.PostEvent(self._notify_window, SentThroughApp(False))
                    self._msg = ""
                    break
            if self._want_abort:
                print("Closed Server.")
                break

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

    def run_server(self, host, port):
        # Handle all incoming connections by spawning worker threads.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        print("Bind successful: " + host)
        server.listen(5)

        while True:
            t = threading.Thread(target=self.handle_connection, args=server.accept())
            t.daemon = True
            t.start()

    def handle_connection(self, client, address):
        print("Client accepted from", address)
        client.settimeout(0.1)
        msg = client.recv(1024).decode("UTF-8")
        # print(msg)
        decrypted_msg = cipher_key.decrypt(msg).decode("UTF-8")  # Decrypt message
        # print(decrypted_msg)
        wx.PostEvent(self._notify_window, ReceiveMessage(decrypted_msg))

    def send_message(self, msg):
        # send_message worker thread.
        # Method for use by main thread to signal a send_message
        self._msg = msg
        # print("Event triggered")
        # print(self._msg)


# GUI --------------------------------------------------------------------------------------
class StatusText(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Status text
        self.status = wx.StaticText(self, label="", style=wx.BORDER_NONE)
        self.status.SetBackgroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))

        # Bind
        EVT_SENT_THROUGH_APP(self, self.change_status)  # Set event for receive message

        # sizer
        self.status_sizer = wx.BoxSizer()
        self.status_sizer.Add(self.status, 1, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.status_sizer)

    def change_status(self, event):
        if event:
            self.status.SetLabelText("Sent via messenger app.")
        else:
            self.status.SetLabelText("Sent via Windows popup.")
        self.status_sizer.Layout()


class LogPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        self.panel = self
        self.SetupScrolling(self, scrollToTop=False)

        # Font Height
        self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.dc = wx.ScreenDC()
        self.dc.SetFont(self.font)
        self.single_height = self.dc.GetMultiLineTextExtent('')

        # Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
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
            u = PC_Local_Name
        u += ': '
        message_sizer = wx.BoxSizer()

        # Chat log - Names
        ui_name = wx.TextCtrl(self, value=u,
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL | wx.BORDER_NONE | wx.TE_RIGHT)
        ui_name.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        # Had to move foreground color to after it gets added to the panel so the color was right (otherwise was reset)
        ui_name.SetMinSize(wx.Size(50, 10))
        ui_name.SetFont(self.font)
        message_sizer.Add(ui_name, 0, wx.EXPAND)

        # Chat log - Messages
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL | wx.BORDER_NONE | wx.TE_AUTO_URL | wx.TE_BESTWRAP
        ui_message = ExpandoTextCtrl(self, value=msg, style=style)
        ui_message.SetBackgroundColour(wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE))
        # Had to move foreground color to after it gets added to the panel so the color was right (otherwise was reset)
        ui_message.SetFont(self.font)
        message_sizer.Add(ui_message, 1, wx.ALL)
        # self.Bind(EVT_ETC_LAYOUT_NEEDED, self.OnRefit, ui_message)

        self.main_sizer.Add(message_sizer, flag=wx.TOP | wx.EXPAND)
        ui_name.SetForegroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))
        ui_message.SetForegroundColour(wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE))
        # self.main_sizer.Show(message_sizer, show=False, recursive=True)
        # self.main_sizer.Layout()
        # self.Layout()
        self.SetupScrolling(scrollToTop=False)
        self.Scroll(0, 10000000)
        # self.Fit()

    def OnRefit(self):
        # The Expando control will redo the layout of the
        # sizer it belongs to, but sometimes this may not be
        # enough, so it will send us this event, so we can do any
        # other layout adjustments needed.  In this case we'll
        # just resize the frame to fit the new needs of the sizer.
        self.Fit()


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

    def send_message(self, event):
        msg = self.text_ctrl.GetValue()
        if msg:
            self.function.append_chat(msg)
            self.text_ctrl.Clear()
            worker.send_message(PC_Local_Name + u_separator + msg)

    def key_code(self, event):
        unicodeKey = event.GetUnicodeKey()
        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            self.text_ctrl.WriteText('\n')
            # print("Shift + Enter")
        elif unicodeKey == wx.WXK_RETURN:
            self.send_message(None)
            # print("Just Enter")
        else:
            event.Skip()
            # print("Any other character")


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=f'Chatting with {PC_Other_Name}', name='Local Instant Messenger')
        self.temp_file = None
        self.sha_github = None
        self.queue_abort = queue.Queue()
        self.SetDoubleBuffered(True)

        # Remember window size and position
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._persistMgr = wx.lib.agw.persist.PersistenceManager.Get()
        _configFile = my_data_dir / 'persist-saved-cfg'
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print("No config file")

        # Panels
        main_panel = wx.Panel(self)
        self.status_text = StatusText(main_panel)
        self.sub_panel_Log = LogPanel(main_panel)
        self.sub_panel_Send = SendPanel(main_panel)
        self.SetIcon(wx.Icon(icon))  # App icon
        # Set Update variable to false
        with open(pkl_update, 'wb') as f:
            pickle.dump(False, f)

        # Set up event handler for any worker thread results
        global worker
        worker = None  # And indicate we don't have a worker thread yet

        # Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.status_text, 0, wx.EXPAND, 5)
        main_sizer.Add(self.sub_panel_Log, 1, wx.EXPAND, 5)
        main_sizer.Add(self.sub_panel_Send, 0, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)
        self.OnStart()  # Start chat server
        self.SetMinSize(wx.Size(300, 300))

        # Bind
        EVT_RECEIVE_MSG(self, self.ReceiveMsg)  # Set event for receive message

    def OnStart(self):
        global worker
        if not worker:
            worker = SocketWorkerThread(self, self.queue_abort)
        self.CheckForUpdate()

    def ReceiveMsg(self, event):
        if type(event.data) is bool:
            self.status_text.change_status(event.data)
        else:
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
                              app_path, app_path,  # double vars intentional. One is current, other is new (same place).
                              pkl_sha, self.sha_github,
                              pkl_update]
                             )
            print("Closing main app.")
        self.Destroy()
        event.Skip()
        print("Skip")

    def CheckForUpdate(self):
        try:
            # Get GitHub sha value:
            url_sha = 'https://api.github.com/repos/LoganAC34/InstantMessaging/contents/Local_Instant_Messenger.exe'
            session = requests.Session()
            sha_github = session.get(url_sha, timeout=1).json()
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

                # Download GitHub file
                url_download = 'https://raw.githubusercontent.com/LoganAC34/' \
                               'InstantMessaging/master/Local_Instant_Messenger.exe'
                self.temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(url_download))
                print(self.temp_file)

                # Set Update variable to True
                with open(pkl_update, 'wb') as f:
                    pickle.dump(True, f)

                # Download file
                t = threading.Thread(target=self.DownloadUpdate, args=[url_download, self.temp_file])
                t.daemon = True
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
        update_popup_icon = wx.Icon(icon)
        update_popup.SetIcon(update_popup_icon)
        update_popup.Show()

        # Download current file
        while True:
            try:
                temp = SpooledTemporaryFile()
                session = requests.Session()
                resp = session.get(url_download)
                temp.write(resp.content)
                temp.seek(0)

                # Write to file
                with open(temp_file, 'wb') as local_file:
                    local_file.write(resp.content)

                # Set Update variable to True
                with open(pkl_update, 'wb') as f:
                    pickle.dump(True, f)

                # Notification about update
                update_popup.Destroy()
                update_popup = wx.adv.NotificationMessage(title='Download Complete!',
                                                          message="Close the program to use updated version.")
                update_popup.SetIcon(update_popup_icon)
                update_popup.Show()
                print("Done.")
                break
            except Exception as e:
                print("Download failed. Trying again.")
                print(e)
                pass
        update_popup.Close()
        update_popup.Destroy()
        update_popup_icon.Destroy()

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
    frame.SetWindowStyle(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
    frame.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
    app.MainLoop()
    app.Destroy()
    del app
    print("Closed main app.")
