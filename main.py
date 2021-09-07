from tkinter import *
from tkinter import ttk
from link import *
import socket
from _thread import *
import queue

nickname_global = "shocker" # Hardcoded, should be the first thing a user sets up when opening the app
connected_users = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.log = Text(mainframe, height=25, width=200, bg="gray", state=DISABLED, cursor='')
        self.log.grid(column=2, row=1, sticky=(W,E))
        self.vsb = Scrollbar(mainframe, orient="vertical", command=self.log.yview)
        self.vsb.grid(column=3, row=1, sticky=(N, S))

        # Messsage box 
        self.message = StringVar()
        message_entry = ttk.Entry(mainframe, width=20, textvariable=self.message)
        message_entry.grid(column=2, row=2, sticky=(W, E))

        # Button removed for aestetic purposes
        #ttk.Button(mainframe, text="Send Message", command=send_message).grid(column=2, row=3, sticky=(E))

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        message_entry.focus()
        root.bind("<Return>", self.send_message)

        start_new_thread(listen, ())

    def send_message(self, *args):
        try:
            if self.message.get() != '':
                #self.log.configure(state=NORMAL)
                #self.log.insert(END, str(nickname_global + ": " + self.message.get() + '\n'))
                #self.log.see(END)
                #self.log.configure(state=DISABLED)
                server.send(str(nickname_global + ": " + self.message.get()).encode(encoding='utf-8'))
                self.message.set('')
        except Exception as e:
            print(e)
    
    def update_log(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
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
            Label(self.mainframe, textvariable=self.user_names[idx]).grid(column=0, row=1+idx, sticky=(W,E))


class MainApp:
    def __init__(self, root):
        self.queue = queue.Queue()
        self.root = root

    def setup(self, server_ip, nickname):
        # Connecting
        IP_address = server_ip#"127.0.0.1"
        Port = 11066
        server.connect((IP_address, Port))
        
        global nickname_global
        nickname_global = nickname
        connected_users.append(nickname)
        self.root = Tk()
        self.root.title("Dissension")
        self.root.minsize(600,400)
        self.root.wm_resizable(False, False)
        self.textChat = TextChat(self.root, self.queue)
        voiceChat = VoiceChat(self.root)
        voiceChat.refresh_user_list()

        self.periodicCall()

        return self.root
    
    def getTextChat(self):
        return self.textChat
    
    def push_to_queue(self, message):
        self.queue.put(message)
    
    def periodicCall(self):
        self.textChat.update_log()
        self.root.after(100, self.periodicCall)

def listen():
    while True:
        message = server.recv(2048)
        main_app.push_to_queue(message.decode())
    #    sockets_list = [server]
    #    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
    #    print("da li ovo sad kao radi")
    #    for socks in read_sockets:
    #        #if socks == server:
    #        message = socks.recv(2048)
    #        print(message)
    #        print("Primio sam makar nesto jebem li ga")

link_root = Tk()
main_app = MainApp(link_root)
link_root.title("Link")
link_root.minsize(200,100)
link_root.wm_resizable(False, False)
link_gui = Link(link_root, main_app)
link_root.mainloop()