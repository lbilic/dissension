from tkinter import *
from tkinter import ttk

class Link:
    def __init__(self, root, mainapp):
        self.mainapp = mainapp
        self.root = root
        # Main frame configuration
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=1, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Server address
        Label(mainframe, text="Server address: ").grid(column=0, row=0, sticky=(W, E))

        self.server_ip = StringVar()
        server_entry = ttk.Entry(mainframe, width=20, textvariable=self.server_ip)
        server_entry.grid(column=3, row=0, sticky=(W, E))

        Label(mainframe, text="Nickname: ").grid(column=0, row=1, sticky=(W, E))
        self.nickname = StringVar()
        nickname_entry = ttk.Entry(mainframe, width=20, textvariable=self.nickname)
        nickname_entry.grid(column=3, row=1, sticky=(W, E))

        Button(mainframe, text="Connect", command=self.connect).grid(column=1, rows=2, sticky=(S))

        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        server_entry.focus()
        root.bind("<Return>", self.connect)

    def connect(self, *args):
        self.root.destroy()
        self.mainapp.setup(self.server_ip.get(), self.nickname.get())