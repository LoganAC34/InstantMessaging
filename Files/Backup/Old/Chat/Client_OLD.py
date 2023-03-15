import socket
client = socket.socket()
ip = socket.gethostbyname('CADD-13')
user = "Tyler?>:"
port = 3434

connected = False
try:
    client.connect((ip, port))
except:
    print("Server.py not connected")
else:
    connected = True
    print("Connect to server: ", ip)
valid = False
while not valid:
    try:
        msg = user + str(input("Enter your message to send: "))
    except:
        print("Invalid input format")
    else:
        to_send = msg.encode("UTF-8")
        client.send(to_send)
