import json
import socket
import subprocess
import threading
import time

from cryptography.fernet import Fernet

from Files import Config


# SERVER ----------------------------------------------------------------------------------------
class SocketWorkerThread(threading.Thread):
    """Worker Thread Class."""
    print("Server Started")

    def __init__(self, queue_from_app, queue_to_app):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)

        self.remote_override = None
        self.local_host = None
        self.remote_host = None
        self.local_name = None
        self.remote_name = None

        # self.u_separator = '?>:'
        # Encryption
        key = b'zBfp5pkJ_-UniuIQI0dzMuf3mTIm6DRkpURXoZpA-Yo='
        self.cipher_key = Fernet(key)

        # Start server
        self.queue_from_app = queue_from_app
        self.queue_to_app = queue_to_app
        self._msg = ""
        self._user = ""
        self.daemon = True
        self.start()

    def run(self):
        """Run Worker Thread."""
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.update_variables()
        receive_port = 3434
        send_port = 3434
        t = threading.Thread(target=self.run_server, args=(self.local_host, receive_port))
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.01)
            if self._user and self._msg:
                data = {'user': self._user, 'message': self._msg}
                data = json.dumps(data)
                encrypted_msg = self.cipher_key.encrypt(data.encode())  # Encrypt message

                while True:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        print("Connecting to " + self.remote_host + ":" + str(send_port))
                        client.settimeout(0.1)
                        client.connect((self.remote_host, send_port))
                        client.send(encrypted_msg)

                        print(self._msg)
                        out = {'function': 'status', 'args': "Sent via messenger app."}
                        self.queue_to_app.put(out)
                    except Exception as e:
                        print(e)
                        batchMessage = f'{self._user}: {self._msg}'
                        batchMessage = batchMessage.replace('\n', ' ')
                        subprocess.call(f'msg /SERVER:{self.remote_host} * /TIME:60 "{batchMessage}"', shell=True)
                        out = {'function': 'status', 'args': "Sent via Windows popup."}
                        self.queue_to_app.put(out)

                    self._msg = ""
                    break

    def run_server(self, host, port):
        # Handle all incoming connections by spawning worker threads.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        print("Bind successful: " + host)
        server.listen(5)

        while True:
            time.sleep(0.01)
            t = threading.Thread(target=self.handle_connection, args=server.accept())
            t.daemon = True
            t.start()

    def handle_connection(self, client, address):
        print("Client accepted from", address)
        client.settimeout(0.1)

        msg = client.recv(1024).decode("UTF-8")
        decrypted_msg = self.cipher_key.decrypt(msg).decode("UTF-8")  # Decrypt message
        # print(decrypted_msg)

        data = json.loads(decrypted_msg)
        if self.remote_override:
            user = self.remote_name
        else:
            user = data['user']
        message = data['message']

        out = {'function': 'message', 'args': {'user': user, 'message': message}}
        self.queue_to_app.put(out)

    def send_message(self, user, msg):
        self._msg = msg
        self._user = user
        # print("Event triggered")
        # print(self._msg)

    def update_variables(self):
        self.remote_host = Config.get_user_info('device_name', 'remote')
        self.remote_name = Config.get_user_info('alias', 'remote')
        self.remote_override = Config.get_user_info('override', 'remote')
        self.local_name = Config.get_user_info('alias', 'local')
        print("Local PC: " + self.local_host + " - " + self.local_name)
        print("Remote PC: " + self.remote_host + " - " + self.remote_name)
