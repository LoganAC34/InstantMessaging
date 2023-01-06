import socket
import struct
import sys

server_address = ('CADD-13', 4000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)
connected = False
while True:
    if not connected:
        print("Connected")
        connected = True
    data, address = sock.recvfrom(4000)
    print(address + ": " + data)
