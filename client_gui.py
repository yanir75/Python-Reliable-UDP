import tkinter as tk
from threading import Thread

from client import Client


def connect(window, client, name):
    client.connect(name)
    window.destroy()
    # create a window
    client_window = tk.Tk()
    client_window.title("Client")
    client_window.geometry("600x600")
    # Disconnect button to disconnect from server
    disconnect_button = tk.Button(client_window, text="Disconnect", command=lambda: disconnect(client_window, client),
                                  height=4, width=85)
    disconnect_button.place(x=0, y=530)
    # get users button from server
    get_users_button = tk.Button(client_window, text="Get Users", command=lambda: client.get_users(), height=2,
                                 width=42)
    get_users_button.place(x=0, y=0)
    # get files button from server
    get_files_button = tk.Button(client_window, text="Get Files", command=lambda: client.get_files(), height=2,
                                 width=42)
    get_files_button.place(x=300, y=0)
    # two input boxes and button sending information to server
    # add two labels above the input boxes
    tk.Label(client_window, text="To (Type all)").place(x=5, y=470)
    tk.Label(client_window, text="Message").place(x=95, y=470)
    name = tk.Entry(client_window, width=10)
    msg = tk.Entry(client_window, width=70)
    name.place(x=10, y=495, height=30)
    msg.place(x=100, y=495, height=30)
    send_button = tk.Button(client_window, text="Send", command=lambda: client.set_msg(msg.get(), name.get()), width=8)
    send_button.place(x=530, y=493, height=32)

    # label for displaying messages
    tk.Label(client_window, text="Messages").place(x=0, y=50)
    # text box for displaying messages
    text_box = tk.Text(client_window, width=70, height=20, state="disabled")
    text_box.place(x=0, y=70)
    # scrollbar for text box
    scrollbar = tk.Scrollbar(client_window)
    scrollbar.place(x=565, y=70, height=325)
    scrollbar.config(command=text_box.yview)
    client.funcs.append(lambda message: update_chat(text_box, message))
    client_window.mainloop()


def update_chat(text_box, msg):
    text_box.config(state="normal")
    msg = msg.split("<")
    for m in msg:
        if len(m) > 0:
            if m[-1] == ">":
                text_box.insert(tk.END, m[:-1] + "\n")
            else:
                text_box.insert(tk.END, m + "\n")
    text_box.config(state="disabled")
    text_box.see(tk.END)


def disconnect(window, client):
    client.disconnect()
    window.destroy()


cl = Client()
# Create a window
window = tk.Tk()
window.title("Client")
window.geometry("400x400")
# get input from user
input_value = tk.StringVar()
# create a label
label = tk.Label(window, text="Connect to server: ")
# create a text box
entry = tk.Entry(window, textvariable=input_value)
# create a button


button = tk.Button(window, text="Connect", command=lambda: connect(window, cl, input_value.get()))
# pack the widgets
label.pack()
entry.pack()
button.pack()
# start the main loop
# create new window and close current one

window.mainloop()