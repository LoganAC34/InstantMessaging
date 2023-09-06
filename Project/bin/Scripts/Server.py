import json
import socket
import subprocess
import threading
import time
from datetime import datetime

from cryptography.fernet import Fernet

from Project.bin.Scripts import Config
from Project.bin.Scripts.Global import GlobalVars


# SERVER ----------------------------------------------------------------------------------------
class SocketWorkerThread(threading.Thread):
    """Worker Thread Class."""
    print("Server Started")

    def __init__(self, queue_from_app, queue_to_app):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)

        self.remote_override = None
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.remote_host = None
        self.local_name = None
        self.remote_name = None
        self.local_name_conn_test = '!connection!'

        # self.u_separator = '?>:'
        # Encryption
        key = b'zBfp5pkJ_-UniuIQI0dzMuf3mTIm6DRkpURXoZpA-Yo='
        self.cipher_key = Fernet(key)

        # Start server
        self.out_data = None
        self.in_data = None
        self.queue_from_app = queue_from_app
        self.queue_to_app = queue_to_app
        self.daemon = True

    def start_server(self):
        self.start()

    def run(self):
        """Run Worker Thread."""
        self.update_variables()
        receive_port = 3434
        send_port = 3434
        t = threading.Thread(target=self.run_server, args=(self.local_host, receive_port))
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.01)
            current_time = datetime.now()
            current_time_formatted = f"{current_time.hour}:{current_time.minute}:{current_time.second}:{current_time.microsecond}"

            if self.out_data:
                # data = {'user': self._user, 'message': self._msg}
                # {'function': 'message', 'args': {'user': user, 'message': msg}}
                function = self.out_data['function']
                encrypted_msg = self.cipher_key.encrypt(json.dumps(self.out_data).encode())  # Encrypt message
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if function == 'message':
                    print("Sending message to " + self.remote_host + ":" + str(send_port))
                    print(self.out_data['args']['message'])
                elif function == 'status':
                    print(f"Testing connection to {self.remote_host}:{str(send_port)} [{current_time_formatted}]")
                elif function == 'typing':
                    print("Telling " + self.remote_host + ":" + str(send_port) + " You're typing.")

                try:
                    client.settimeout(0.1)
                    client.connect((self.remote_host, send_port))
                    client.send(encrypted_msg)
                    via = 'app'

                except TimeoutError:
                    via = 'Windows popup'
                    if function == 'message':
                        args = self.out_data['args']
                        user = args['user']
                        msg = args['message']
                        batchMessage = f'{user}: {msg}'
                        batchMessage = batchMessage.replace(GlobalVars.lineBreak, ' ')
                        subprocess.call(f'msg /SERVER:{self.remote_host} * /TIME:60 "{batchMessage}"', shell=True)

                # Status
                action = 'Will send'
                if function == 'message':
                    action = 'Sent'
                out = {'function': 'status', 'args': [action, self.remote_host, via]}
                self.queue_to_app.put(out)

            self.out_data = None

    def run_server(self, host, port):
        # Handle all incoming connections by spawning worker threads.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        print("Bind successful: " + host)
        server.listen(5)

        while True:
            time.sleep(0.001)
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

        function = data['function']
        args = data['args']
        if function == 'message':
            if self.remote_override:
                data['args']['user'] = self.remote_name
            print(data)
        elif function == 'status':
            return

        self.queue_to_app.put(data)

    def send_message(self, user, msg):
        self.out_data = {'function': 'message', 'args': {'user': user, 'message': msg}}
        # print("Event triggered")
        # print(self.out_data)

    def connection_status(self, user=None):
        self.out_data = {'function': 'status', 'args': user}
        # print("Event triggered")
        # print(self.out_data)

    def typing(self, user):
        self.out_data = {'function': 'typing', 'args': user}
        # print("Event triggered")
        # print(self.out_data)

    def update_variables(self):
        self.remote_host = Config.get_user_info('device_name', 'remote')
        self.remote_name = Config.get_user_info('alias', 'remote')
        self.remote_override = Config.get_user_info('override', 'remote')
        self.local_name = Config.get_user_info('alias', 'local')
        print("Local PC: " + self.local_host + " - " + self.local_name)
        print("Remote PC: " + self.remote_host + " - " + self.remote_name)
