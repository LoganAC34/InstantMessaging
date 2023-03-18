import socket
import subprocess
import threading

import wx
from cryptography.fernet import Fernet

u_separator = '?>:'
key = b'zBfp5pkJ_-UniuIQI0dzMuf3mTIm6DRkpURXoZpA-Yo='
cipher_key = Fernet(key)

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
    print("Server.py Started")

    def __init__(self, remote_host, notify_window, queue_abort):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._want_abort = None
        self._queue_abort = queue_abort
        self._notify_window = notify_window
        self.remote_host = remote_host
        self._msg = ""
        self.daemon = True
        self.start()

    def run(self):
        """Run Worker Thread."""
        local_host = socket.gethostbyname(socket.gethostname())
        receive_port = 3434
        send_port = 3434
        t = threading.Thread(target=self.run_server, args=(local_host, receive_port))
        t.daemon = True
        t.start()

        while True:
            if self._msg:
                while True:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        print("Connecting to " + self.remote_host + ":" + str(send_port))
                        client.settimeout(0.1)
                        client.connect((self.remote_host, send_port))
                        encrypted_msg = cipher_key.encrypt(self._msg.encode())  # Encrypt message
                        client.send(encrypted_msg)
                        print(self._msg)
                        wx.PostEvent(self._notify_window, SentThroughApp(True))
                    except Exception as e:
                        print(e)
                        batchMessage = self._msg.replace(u_separator, ': ')
                        batchMessage = batchMessage.replace('\n', ' ')
                        subprocess.call(f'msg /SERVER:{self.remote_host} * /TIME:60 "{batchMessage}"', shell=True)
                        wx.PostEvent(self._notify_window, SentThroughApp(False))
                    self._msg = ""
                    break
            if self._want_abort:
                print("Closed Server.py.")
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
