import socket

ip = socket.gethostbyname('CADD-13')


class Client():
    def __init__(self, Adress=(ip, 5000)):
        self.s = socket.socket()
        self.s.connect(Adress)


c = Client()
