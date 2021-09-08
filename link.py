from tkinter import *
from tkinter import ttk

class Link:
    def __init__(self, root, mainapp):
        self.mainapp = mainapp
        self.root = root
        # Main frame configuration
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=1, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Server address
        Label(self.mainframe, text="Server address: ").grid(column=0, row=0, sticky=(W))
        self.server_ip = StringVar()
        server_entry = ttk.Entry(self.mainframe, width=20, textvariable=self.server_ip)
        server_entry.grid(column=3, row=0, sticky=(W, E))

        # Nickname
        Label(self.mainframe, text="Nickname: ").grid(column=0, row=1, sticky=(W))
        self.nickname = StringVar()
        nickname_entry = ttk.Entry(self.mainframe, width=20, textvariable=self.nickname)
        nickname_entry.grid(column=3, row=1, sticky=(W, E))

        Button(self.mainframe, text="Connect", command=self.connect).grid(column=1, row=3, sticky=(S))

        for child in self.mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        server_entry.focus()
        root.bind("<Return>", self.connect)

    def connect(self, *args):
        nickname = self.nickname.get()
        nickname_len = len(nickname)
        if not nickname.isalnum() or nickname_len < 2 or nickname_len > 16:
            Label(self.mainframe, text="Nickname must be between 2 and 16 characters in length.", fg="red").grid(column=3, row=2, sticky=(E))
        else:
            self.root.destroy()
            self.mainapp.setup(self.server_ip.get(), self.nickname.get())