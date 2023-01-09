import socket, time, os, random

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
        print(clientsocket.recv(1024))
        valid = False
        while not valid:
            try:
                msg = str(input("Enter your message to send: "))
            except:
                print("Invalid input format")
            else:
                valid = True
        clientsocket.send(msg.encode("UTF-8"))
