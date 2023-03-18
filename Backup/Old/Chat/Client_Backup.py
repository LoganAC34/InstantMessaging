import socket
client = socket.socket()
ip = socket.gethostbyname('CADD-13')
port = 3434
try:
    client.connect((ip, port))
except:
    print("Server.py not connected")
else:
    print("Connect to server: ", ip)
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
