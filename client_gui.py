import os
import tkinter as tk
from tkinter import font

from client import Client


def connect(to_close_window, client, name,ip):
    client.connect(name,ip)
    to_close_window.destroy()
    # create a window
    client_window = tk.Tk()
    client_window.title("Chat room")
    client_window.geometry("600x600")
    client_window['background'] = '#86daeb'
    # Disconnect button to disconnect from server
    disconnect_button = tk.Button(client_window, text="Disconnect", command=lambda: disconnect(client_window, client),
                                  width=29, fg='black', bg='#6faaf8',
                                  font=font.Font(size=25, weight='bold', family='courier'))
    disconnect_button.place(x=5, y=530)

    # get users button from server
    get_users_button = tk.Button(client_window, text="Get Users", command=lambda: client.get_users(),
                                 width=20, fg='black', bg='#6faaf8',
                                 font=font.Font(size=18, weight='bold', family='courier'))
    get_users_button.place(x=5, y=0)

    # get files button from server
    get_files_button = tk.Button(client_window, text="Get Files", command=lambda: client.get_list_file(),
                                 width=20, fg='black', bg='#6faaf8',
                                 font=font.Font(size=18, weight='bold', family='courier'))
    get_files_button.place(x=305, y=0)

    # two input boxes and button sending information to server
    # add two labels above the input boxes
    tk.Label(client_window, text="To (Type all)", bg='#86daeb').place(x=5, y=470)
    tk.Label(client_window, text="Message", bg='#86daeb').place(x=95, y=470)
    name = tk.Entry(client_window, width=10)
    msg = tk.Entry(client_window, width=70)
    name.place(x=10, y=495, height=30)
    msg.place(x=100, y=495, height=30)
    send_button = tk.Button(client_window, text="Send",
                            command=lambda: client.set_msg(msg.get(), name.get()),
                            width=8, fg='black', bg='#6faaf8')
    send_button.place(x=530, y=493, height=32)

    # download file button to download file from server
    tk.Label(client_window, text="File name to download", bg='#86daeb',
             font=font.Font(size=11, family='courier')).place(x=5, y=415)

    download = tk.Entry(client_window, width=85)
    download.place(x=10, y=437, height=30)
    download_button = tk.Button(client_window, text="Download", command=lambda: client.download(download.get()),
                                width=8, fg='black', bg='#6faaf8')
    download_button.place(x=530, y=438, height=32)

    # label for displaying messages
    tk.Label(client_window, text="Messages", bg='#86daeb', font=font.Font(size=11, family='courier')).place(x=5, y=50)
    # text box for displaying messages
    text_box = tk.Text(client_window, width=70, height=20, state="disabled")
    text_box.place(x=5, y=70)
    # scrollbar for text box
    scrollbar = tk.Scrollbar(client_window)
    scrollbar.place(x=570, y=70, height=325)
    scrollbar.config(command=text_box.yview)
    # functions to activate on each message
    client.funcs.append(lambda message: update_chat(text_box, message,client_window,client))
    client.activate.append(lambda: enable_button(download_button))
    client.deactivate.append(lambda: disable_button(download_button))
    # on exit close the window and disconnect from server
    client_window.protocol("WM_DELETE_WINDOW", lambda: disconnect(client_window, client))
    client_window.mainloop()


def update_chat(text_box, msg, client_window, client):
    # update the text box according to received message
    text_box.config(state="normal")
    msg = msg.split("<")
    for m in msg:
        if m == "disconnected>":
            os._exit(0)
        if len(m) > 0:
            if m[-1] == ">":
                text_box.insert(tk.END, m[:-1] + "\n")
            else:
                text_box.insert(tk.END, m + "\n")
    text_box.config(state="disabled")
    text_box.see(tk.END)


def disconnect(close_window, client):
    client.disconnect()
    close_window.destroy()
    os._exit(0)


def start():
    cl = Client()
    # Create a window
    window = tk.Tk()
    window.title("Connect window")
    window['background'] = '#86daeb'
    window.geometry("300x100")
    # get input from user
    input_value = tk.StringVar()
    # create a label
    label = tk.Label(window, text="Enter your name: ", bg='#86daeb', font=font.Font(size=11, family='courier'))
    label.place(x=15, y=20)
    # create a text box
    entry = tk.Entry(window, textvariable=input_value, width=25)
    # create a button
    ip_entry = tk.Entry(window, width=25)
    ip_entry.place(x=15, y=60)
    # default string for entry
    ip_entry.insert(0, "127.0.0.1")
    button = tk.Button(window, text="Connect", command=lambda: connect(window, cl, input_value.get(),ip_entry.get()), height=7,
                       fg='black',
                       bg='#6faaf8', font=font.Font(size=14, weight='bold', family='courier'))
    # pack the widgets
    entry.pack(side=tk.LEFT, padx=15, pady=20)
    button.pack(side=tk.RIGHT, padx=15, pady=20)
    # start the main loop
    # create new window and close current one

    window.mainloop()


def disable_button(button):
    button['state'] = 'disabled'


def enable_button(button):
    button['state'] = 'normal'


start()
