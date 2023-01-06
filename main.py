import socket, time, os, random


class Server():
    def __init__(self, Address=('', 5000), MaxClient=1):
        self.s = socket.socket()
        self.s.bind(Address)
        self.s.listen(MaxClient)

    def WaitForConnection(self):
        self.Client, self.Adr = (self.s.accept())
        print('Got a connection from: ' + str(self.Client) + '.')


s = Server()
s.WaitForConnection()
