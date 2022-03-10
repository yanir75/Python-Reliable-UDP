import tkinter as tk
from tkinter import font
from threading import Thread
from server import Server


def start():
    server = Server()
    # Create a window
    window = tk.Tk()
    window.title("Server")
    window['background'] = '#86daeb'
    window.geometry("600x600")
    # get input from user
    # create a label
    # create a text box
    # create a button

    button = tk.Button(window, text="Start", command=lambda: Thread(target=server.run).start(), width=52, height=3,
                       fg='black',
                       bg='#6faaf8', font=font.Font(size=14, weight='bold', family='courier'))
    # disconnect all button
    # disable the button after click
    server.disable.append(lambda: disable_button(button))
    # pack the widgets
    # button.pack(side=tk.TOP, padx=15, pady=20)
    button.place(x=5, y=50)
    text_box = tk.Text(window, width=70, height=27, state="disabled")
    text_box.place(x=5, y=150)
    scrollbar = tk.Scrollbar(window, command=text_box.yview)
    scrollbar.place(x=575, y=148, height=440)
    server.funcs.append(lambda msg: update_chat(text_box, msg))

    # add disconnect button
    dis_button = tk.Button(window, text="Disconnect", command=lambda: server.disconnect_all(),fg='black',
                       bg='#6faaf8', font=font.Font(size=14, weight='bold', family='courier'))
    dis_button.place(x=20, y=10, width=550)
    # on exit, disconnect all
    window.protocol("WM_DELETE_WINDOW", lambda: server.disconnect_all())
    # start the main loop
    # create new window and close current one

    window.mainloop()


def update_chat(text_box, msg):
    # update the text box according to received message
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


def run(server):
    server.run()


def disable_button(button):
    button.config(state="disabled")


start()
