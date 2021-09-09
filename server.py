import socket
from threading import *
from _thread import *

HANDSHAKE_MESSAGE = "mysecretfornow"
BUFFER_SIZE = 1024
BROADCASTING_PORT = 11067
TEXT_LISTENING_PORT = 3480
VOICE_LISTENING_PORT = 3481

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
HOST_IP = s.getsockname()[0]
s.close()

# Text Server
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
text_server.bind((HOST_IP, TEXT_LISTENING_PORT))
text_server.listen(100)

list_of_clients = []
client_names = []

# Voice server
voice_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voice_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
voice_server.bind((HOST_IP, VOICE_LISTENING_PORT))

def clientthread(conn, addr):
    keepAlive = 1
    while keepAlive:
        try:
            message = conn.recv(BUFFER_SIZE)
            if message:
                if HANDSHAKE_MESSAGE in message.decode():
                    connected_user = message.decode().split(HANDSHAKE_MESSAGE)[0].strip()
                    if connected_user != client_names:
                        client_names.append(connected_user)
                        userlist = ';'.join(client_names) + HANDSHAKE_MESSAGE
                        broadcast_message(userlist)
                else:
                    print("<" + addr[0] + ">" + message.decode())
                    message_to_send = message.decode()
                    broadcast_message(message_to_send)
            else:
                remove(conn)
        except Exception as e:
            conn.close()
            remove(conn)
            keepAlive = 0

def broadcast_message(message):
    for client in list_of_clients:
        try:
            client.send(message.encode())
        except Exception as e:
            print(e)
            client.close()

            # if the link is broken, we remove the client
            remove(client)
 
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
 
while True:

    conn, addr = text_server.accept()
    #text_server.listen()

    list_of_clients.append(conn)

    print (addr[0] + " connected")

    start_new_thread(clientthread,(conn,addr))

    # New code, switching from TCP to UDP

    #message, addr = voice_server.recvfrom(BUFFER_SIZE)
    #if addr not in list_of_clients:
    #    list_of_clients.append(addr)
    #if HANDSHAKE_MESSAGE in message.decode():
    #    connected_user = message.decode().split(HANDSHAKE_MESSAGE)[0].strip()
    #    if connected_user != client_names:
    #        client_names.append(connected_user)
    #        userlist = ';'.join(client_names) + HANDSHAKE_MESSAGE
    #        broadcast_message(userlist.encode())
    #else:
    #    print("<" + addr[0] + ">" + message.decode())
    #    broadcast_message(message)
    #server.sendto(b"Welcome to Dissension!", addr)
 
conn.close()
server.close()