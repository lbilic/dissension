from tkinter import *
from tkinter import ttk
from link import *
import socket
from _thread import *
import threading, pyaudio
import queue

nickname_global = "" # Hardcoded, should be the first thing a user sets up when opening the app
connected_users = []
recorded_frames = []
received_frames = {}
play_threads = []
HANDSHAKE_MESSAGE = "mysecretfornow"
BUFFER_SIZE = 1024
VOICE_BUFFER_SIZE = 65536
LISTENING_PORT = 11067
TEXT_SENDING_PORT = 3480
VOICE_SENDING_PORT = 3481
SERVER_IP_address = ''

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
LOCAL_IP_ADDRESS = s.getsockname()[0]
s.close()

# Voice chat
voice_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voice_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, VOICE_BUFFER_SIZE)

# Text chat
text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class TextChat:
    def __init__(self, root, queue):
        # Queue for listening
        self.queue = queue

        # Main frame configuration
        mainframe = ttk.LabelFrame(root, text="Text Chat", padding="3 3 12 12")
        mainframe.grid(column=1, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)


        # Chat log
        self.log = Text(mainframe, height=40, width=95, bg="gray", state=DISABLED, cursor='')
        self.log.grid(column=2, row=1, sticky=(W,E))
        self.vsb = Scrollbar(mainframe, orient="vertical", command=self.log.yview)
        self.vsb.grid(column=3, row=1, sticky=(N, S))

        # Messsage box 
        self.message = StringVar()
        message_entry = ttk.Entry(mainframe, width=20, textvariable=self.message)
        message_entry.grid(column=2, row=2, sticky=(W, E))

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        message_entry.focus()
        root.bind("<Return>", self.send_message)

        start_new_thread(listen, ())

    def send_message(self, *args):
        try:
            if self.message.get() != '':
                text_server.send(str(nickname_global + ": " + self.message.get()).encode(encoding='utf-8'))
                self.message.set('')
        except Exception as e:
            print(e)
    
    def update_log(self):
        global connected_users
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if HANDSHAKE_MESSAGE in msg:
                    connected_users_list = msg.replace(HANDSHAKE_MESSAGE, '')
                    connected_users = connected_users_list.strip().split(';')
                else:
                    self.log.configure(state=NORMAL)
                    self.log.insert(END, str(msg + '\n'))
                    self.log.see(END)
                    self.log.configure(state=DISABLED)
            except:
                continue

class VoiceChat:
    def __init__(self, root):
        # Main frame configuration
        self.mainframe = ttk.LabelFrame(root, text="Voice Chat", padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
    
    def on_connect(self):
        self.refresh_user_list()
    
    def on_disconnect(self):
        self.refresh_user_list()
    
    def refresh_user_list(self):
        self.user_names = []
        for idx, user in enumerate(connected_users):
            self.user_names.append(StringVar())
            self.user_names[idx].set(user)
            Label(self.mainframe, textvariable=self.user_names[idx]).grid(column=0, row=1+idx, sticky=(W))


class MainApp:
    def __init__(self, root):
        self.queue = queue.Queue()
        self.audio_change = queue.Queue()
        self.root = root
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        p = pyaudio.PyAudio()
        self.recording_stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE,  input = True, frames_per_buffer = CHUNK)
        self.play_streams = {}
        self.play_stream = p.open(format=FORMAT, channels = CHANNELS, rate = RATE, output = True, frames_per_buffer = CHUNK)
        self.thread_record = threading.Thread(target=record_audio, args=(self.recording_stream,CHUNK))
        self.thread_send = threading.Thread(target=udp_send)
        self.thread_receive = threading.Thread(target = udp_receive, args=(self.play_streams, p))
        #self.thread_play = threading.Thread(target = play, args=(self.play_stream, CHUNK,))

    def setup(self, server_ip, nickname):
        global nickname_global
        global SERVER_IP_address
        global LOCAL_IP_ADDRESS
        nickname_global = nickname

        # Connecting
        SERVER_IP_address = server_ip
        text_server.connect((LOCAL_IP_ADDRESS, TEXT_SENDING_PORT))
        voice_server.bind((LOCAL_IP_ADDRESS, LISTENING_PORT))

        self.thread_record.setDaemon(True)
        self.thread_send.setDaemon(True)
        self.thread_record.start()
        self.thread_send.start()

        self.thread_receive.setDaemon(True)
        #self.thread_play.setDaemon(True)
        self.thread_receive.start()
        #self.thread_play.start()

        # Send login message
        login_message = nickname_global + HANDSHAKE_MESSAGE
        text_server.send(login_message.encode())

        connected_users.append(nickname)
        self.root = Tk()
        self.root.title("Dissension")
        self.root.geometry("1280x720+320+160")
        self.root.minsize(1280,720)
        self.root.wm_resizable(False, False)
        self.textChat = TextChat(self.root, self.queue)
        self.voiceChat = VoiceChat(self.root)
        self.voiceChat.refresh_user_list()

        self.periodicCall()

        return self.root

    def getTextChat(self):
        return self.textChat
    
    def getVoiceChat(self):
        return self.voiceChat
    
    def push_to_queue(self, message, audio=False):
        if audio:
            self.audio_queue.put(message)
        else:
            self.queue.put(message)
    
    def periodicCall(self):
        self.textChat.update_log()
        self.voiceChat.refresh_user_list()
        self.root.after(100, self.periodicCall)

def record_audio(stream, CHUNK):
    while True:
        recorded_frames.append(stream.read(CHUNK))

def udp_send():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if len(recorded_frames) > 0:
            data = recorded_frames.pop(0)
            udp.sendto(data, (SERVER_IP_address, VOICE_SENDING_PORT))
    udp.close()

def udp_receive(play_streams, p):
    while True:
        soundData, addr = voice_server.recvfrom(1024 * 2 * 2) # CHUNK * 2 * channels
        current_user = ''
        try:
            if "user:" in soundData.decode():
                current_user = soundData.decode().split(':')[1]
        except:
            if current_user in received_frames.keys():
                received_frames[current_user].append(soundData)
            else:
                received_frames[current_user] = []
                play_streams[current_user] = p.open(format=pyaudio.paInt16, channels = 2, rate = 44100, output = True, frames_per_buffer = 1024)
                t = threading.Thread(target=play_2, args=(play_streams[current_user], current_user))
                #play_threads.append(t)
                t.start()


    udp.close()

def play(stream, CHUNK):
    BUFFER = 10
    while True:
        for client in received_frames.keys():
            if len(received_frames[client]) == BUFFER:
                while True:
                    if len(received_frames[client]) > 0:
                        stream.write(received_frames[client].pop(0), CHUNK)

def play_2(stream, client):
    BUFFER = 10
    while True:
        if len(received_frames[client]) == BUFFER:
            while True:
                if len(received_frames[client]) > 0:
                    stream.write(received_frames[client].pop(0), 1024)

def write(stream, CHUNK):
    pass

def listen():
    while True:
        message = text_server.recv(BUFFER_SIZE)
        main_app.push_to_queue(message.decode())

def on_closing():
    text_server.close()
    voice_server.close()
    link_root.destroy()

if __name__ == '__main__':
    link_root = Tk()
    link_root.protocol("WM_DELETE_WINDOW", on_closing)
    main_app = MainApp(link_root)
    link_root.title("Link")
    link_root.geometry("320x240+320+160")
    link_root.minsize(320,240)
    link_root.wm_resizable(False, False)
    link_gui = Link(link_root, main_app)
    link_root.mainloop()