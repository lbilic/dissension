import socket
from threading import *
from _thread import *
import wave, pyaudio, time

HANDSHAKE_MESSAGE = "mysecretfornow"
BUFFER_SIZE = 1024
BROADCASTING_PORT = 11067
TEXT_LISTENING_PORT = 3480
VOICE_LISTENING_PORT = 3481
VOICE_SENDING_PORT = 11067

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
received_frames = {}
list_of_client_ips = []

# Voice server
voice_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voice_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

def client_thread_voice(conn, addr):
    CHUNK = 50*1024
    wf = wave.open("test.wav")

    sample_rate = wf.getframerate()
    number_of_frames = int(CHUNK/wf.getsampwidth()/wf.getnchannels())
    data = wf.readframes(number_of_frames)
    while data:
        try:
            voice_server.sendto(data, (addr[0],11067))
            time.sleep(60/wf.getframerate()*number_of_frames/48)
            data = wf.readframes(int(CHUNK/wf.getsampwidth()/wf.getnchannels()))
        except Exception as e:
            print(e)

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
 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
p = pyaudio.PyAudio()

def udp_receive():
    while True:
        soundData, addr = voice_server.recvfrom(CHUNK * 2 * 2) # CHUNK * 2 * channels
        if addr[0] in received_frames.keys():
            received_frames[addr[0]].append(soundData)
        else:
            received_frames[addr[0]] = []

    udp.close()

def broadcast_voice():
    while True:
        for sending_client in received_frames.keys():
            if len(received_frames[sending_client]) > 0:
                frame = received_frames[sending_client].pop(0)
                for client in list_of_client_ips:
                    if True:#client != sending_client:
                        voice_server.sendto(str("user:" + sending_client).encode(), (client, VOICE_SENDING_PORT))
                        voice_server.sendto(frame, (client, VOICE_SENDING_PORT))

if __name__ == '__main__':
    stream = p.open(format=FORMAT, channels = CHANNELS, rate = RATE, output = True, frames_per_buffer = CHUNK)    
    Ts = Thread(target = udp_receive, args=())
    Tr = Thread(target = broadcast_voice, args=())
    Tr.setDaemon(True)
    Ts.setDaemon(True)
    Ts.start()
    Tr.start()
    while True:
        conn, addr = text_server.accept()
        #text_server.listen()

        list_of_clients.append(conn)
        list_of_client_ips.append(addr[0])
        print (addr[0] + " connected")

        start_new_thread(clientthread,(conn,addr))
        #start_new_thread(client_thread_voice, (conn, addr))

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