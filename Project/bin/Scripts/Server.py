import json
import queue
import socket
import struct
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

    def __init__(self, queue_server_and_app):
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
        self.out_data_queue = queue.Queue()
        self.in_data = None
        self.queue_server_and_app = queue_server_and_app
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
            current_time_formatted = (f"{current_time.hour}:{current_time.minute}:"
                                      f"{current_time.second}:{current_time.microsecond}")

            if self.out_data_queue.not_empty:
                # data = {'user': self._user, 'message': self._msg}
                # {'function': 'message', 'args': {'user': user, 'message': msg}}
                out_data = self.out_data_queue.get()
                function = out_data['function']
                encrypted_msg = self.cipher_key.encrypt(json.dumps(out_data).encode("UTF-8"))  # Encrypt message
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if function == 'message':
                    print("Sending message to " + self.remote_host + ":" + str(send_port))
                    print(out_data['args']['message'])
                elif function == 'status':
                    # print(f"Testing connection to {self.remote_host}:{str(send_port)} [{current_time_formatted}]")
                    pass
                elif function == 'typing':
                    # print("Telling " + self.remote_host + ":" + str(send_port) + " You're typing.")
                    pass

                try:
                    client.settimeout(0.1)
                    client.connect((self.remote_host, send_port))
                    encrypted_msg = struct.pack('>I', len(encrypted_msg)) + encrypted_msg
                    client.sendall(encrypted_msg)
                    # client.send(encrypted_msg)
                    via = 'app'

                except TimeoutError:
                    via = 'Windows popup'
                    if function == 'message':
                        args = out_data['args']
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
                self.queue_server_and_app.put(out)

    def run_server(self, host, port):
        # Handle all incoming connections by spawning worker threads.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Trying to connect...")
        connected = False
        while not connected:
            try:
                server.bind((host, port))
                connected = True
            except OSError:
                print("Error connecting!")
                time.sleep(5)
                print("Retrying to connect...")
        print("Bind successful: " + host)
        server.listen(5)

        while True:
            time.sleep(0.001)
            t = threading.Thread(target=self.handle_connection, args=server.accept())
            t.daemon = True
            t.start()

    def handle_connection(self, client, address):
        def recvall(sock, n):
            # Helper function to recv n bytes or return None if EOF is hit
            data = bytearray()
            while len(data) < n:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            return data

        def recv_msg(sock):
            # Read message length and unpack it into an integer
            raw_msglen = recvall(sock, 4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            # Read the message data
            return recvall(sock, msglen).decode("UTF-8")

        print("Client accepted from", address)
        client.settimeout(0.1)

        try:
            # msg = client.recv(1024).decode("UTF-8")
            msg = recv_msg(client)
        except TimeoutError:
            return
        decrypted_msg = self.cipher_key.decrypt(msg).decode("UTF-8")  # Decrypt message
        data = json.loads(decrypted_msg)

        function = data['function']
        args = data['args']
        if function in ['message', 'image']:
            if self.remote_override:
                data['args']['user'] = self.remote_name
            print(data)
        elif function == 'status':
            return

        self.queue_server_and_app.put(data)

    def send_message(self, user, msg):
        self.out_data_queue.put({'function': 'message', 'args': {'user': user, 'message': msg}})
        time.sleep(0.01)
        # print("Event triggered")
        # print(self.out_data_queue)

    def send_image(self, user, image_data):
        self.out_data_queue.put({'function': 'image', 'args': {'user': user, 'image': image_data}})
        time.sleep(0.01)

    def connection_status(self, user=None):
        self.out_data_queue.put({'function': 'status', 'args': user})
        # print("Event triggered")
        # print(self.out_data_queue)

    def typing(self, user):
        self.out_data_queue.put({'function': 'typing', 'args': user})
        # print("Event triggered")
        # print(self.out_data_queue)

    def update_variables(self):
        self.remote_host = Config.get_user_info('device_name', 'remote')
        self.remote_name = Config.get_user_info('alias', 'remote')
        self.remote_override = Config.get_user_info('override', 'remote')
        self.local_name = Config.get_user_info('alias', 'local')
        print("Local PC: " + self.local_host + " - " + self.local_name)
        print("Remote PC: " + self.remote_host + " - " + self.remote_name)
