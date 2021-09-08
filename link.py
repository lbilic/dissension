from tkinter import *
from tkinter import ttk

class Link:
    def __init__(self, root, mainapp):
        self.mainapp = mainapp
        self.root = root
        # Main frame configuration
        self.mainframe = ttk.Frame(root, padding=("75 35 75 35"))
        self.mainframe.grid(column=0, row=0)

        # Server address
        Label(self.mainframe, text="Server address: ").grid(column=0, row=0)
        self.server_ip = StringVar()
        server_entry = ttk.Entry(self.mainframe, width=25, textvariable=self.server_ip)
        server_entry.grid(column=0, row=1)

        # Nickname
        Label(self.mainframe, text="Nickname: ").grid(column=0, row=2)
        self.nickname = StringVar()
        nickname_entry = ttk.Entry(self.mainframe, width=25, textvariable=self.nickname)
        nickname_entry.grid(column=0, row=3)

        Button(self.mainframe, text="Connect", command=self.connect).grid(column=0, row=5)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        server_entry.focus()
        root.bind("<Return>", self.connect)

    def connect(self, *args):
        nickname = self.nickname.get()
        nickname_len = len(nickname)
        if not nickname.isalnum() or nickname_len < 2 or nickname_len > 16:
            Label(self.mainframe, text="Nickname must be between 2 \n and 16 characters in length.", fg="red").grid(column=0, row=4)
        else:
            self.root.destroy()
            self.mainapp.setup(self.server_ip.get(), self.nickname.get())