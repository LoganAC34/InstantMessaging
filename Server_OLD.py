import socket, time, os, random
from threading import Thread
import wx
from Interface import ReceiveMessage

# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname('CADD-13')
        port = 3434
        print(ip)
        try:
            server.bind((ip, port))
        except:
            print("Bind failed")
        else:
            print("Bind successful")
        server.listen(5)
        clientsocket = None
        while True:
            if clientsocket is None:
                print("[Waiting for connection..]")
                (clientsocket, address) = server.accept()
                print("Client accepted from", address)
                msg = "pong"
                clientsocket.send(msg.encode("UTF-8"))
            else:
                print("[Waiting for response...]")
                msg = clientsocket.recv(1024)
                print(msg)

                # Here's where the result would be returned
                #wx.PostEvent(self._notify_window, ReceiveMessage(msg))
                """
                valid = False
                while not valid:
                    try:
                        msg = str(input("Enter your message to send: "))
                    except:
                        print("Invalid input format")
                    else:
                        valid = True
                clientsocket.send(msg.encode("UTF-8"))
                """

            if self._want_abort:
                # Use a result of None to acknowledge the abort (of
                # course you can use whatever you'd like or even
                # a separate event type)
                wx.PostEvent(self._notify_window, ReceiveMessage(None))
                return

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

if __name__ == '__main__':
    WorkerThread.run(WorkerThread(None))
