import sqlite3
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM


def send_message(recipient='CADD-7', message=b"Hello World!"):
    recipient = 'CADD-7'  # Server ip
    port = 4000

    mySocket = socket(AF_INET, SOCK_DGRAM)
    mySocket.connect((recipient, port))

    while True:
        mySocket.send(message)
        #break

if __name__ == '__main__':
    send_message('PyCharm')

