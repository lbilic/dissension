import socket
import sys
from threading import *
from _thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
HANDSHAKE_MESSAGE = "mysecretfornow"

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])

server.bind((IP_address, Port))

server.listen(100)
list_of_clients = []

def clientthread(conn, addr):
    #conn.send(b"Welcome to Dissension!")

    while True:
        try:
            message = conn.recv(2048)
            if message:
                if "mysecretfornow" in message.decode():
                    handshake_message = message.decode()
                    broadcast_message(handshake_message, conn)
                else:
                    print("<" + addr[0] + ">" + message.decode())
                    message_to_send = message.decode()
                    broadcast_message(message_to_send, conn)
            else:
                remove(conn)
        except:
            continue

def broadcast_message(message, connection):
    for client in list_of_clients:
        if True:#client != connection:
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
 
    conn, addr = server.accept()
    #server.listen()

    list_of_clients.append(conn)
 
    print (addr[0] + " connected")

    start_new_thread(clientthread,(conn,addr))
 
conn.close()
server.close()