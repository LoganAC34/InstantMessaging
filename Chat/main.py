import socket
#import Client
#import Server

client = socket.socket()
ip = socket.gethostbyname('CADD-13')
port = 3434
connected = False

try:
    client.connect((ip, port))
except:
    print("No current chat server running")
else:
    print("Connect to server:", ip)
    connected = True

if connected:
    while True:
        print("[Waiting for response...]")
        print(client.recv(1024))
        valid = False
        while not valid:
            try:
                msg = str(input("Enter your message to send: "))
            except:
                print("Invalid input format")
            else:
                valid = True
        to_send = msg.encode("UTF-8")
        client.send(to_send)
else:
    print("Starting Server")
    Server.start()
