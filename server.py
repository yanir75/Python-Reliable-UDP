from socket import *
from threading import *


class Server:
    def __init__(self):
        """
        Create a server and add the needed fields.
        """
        # AF_inet = IPv4 address family and SOCK_STREAM = TCP
        self.socket = socket(AF_INET, SOCK_STREAM)
        # bind the socket to the port number and host address (localhost) and listen for connections (5) at max,
        # at a time
        self.socket.bind(('127.0.0.1', 50002))
        self.socket.listen(5)
        # create a list of clients to store the clients connected to the server
        self.clients = {}

    def run(self):
        """
        Run the server and listen for connections.
        """
        while True:
            # accept a connection from a client
            sock, addr = self.socket.accept()
            # receive the name of the client
            name = sock.recv(1024).decode()
            name = name[10:-1]
            # add the client to the list of clients
            self.send_message_to_all("A new member has entered the chat: " + name)
            self.send_client(sock, "<connected>")
            self.clients[sock] = name
            # create a thread to handle the client
            Thread(target=self.handle_client, args=(sock, name)).start()

    def handle_client(self, sock, name):
        """
        Handle the client and listen for his commands
        """
        while True:
            try:
                # receive the message from the client
                message = sock.recv(1024).decode()
                print(message)
                if message == "<disconnect>":
                    self.send_client(sock, "<disconnected>")
                    raise Exception
                if message == "<get_users>":
                    msg = f'<users_lst><{len(self.clients)}>'
                    for client in self.clients.values():
                        msg += f'<{client}>'
                    msg += '<end>'
                    self.send_client(sock, msg)
                if message.startswith("<set_msg>"):
                    mess = message.split('<')
                    to = mess[2][:-1]
                    msg = mess[3][:-1]
                    for client in self.clients.keys():
                        if self.clients[client] == to:
                            self.send_client(client, f'<{name}:{msg}>')
                if message.startswith("<set_msg_all>"):
                    self.send_message_to_all(f'<{name}:{message[14:-1]}>')
            except Exception as e:
                print(e)
                self.clients.pop(sock)
                sock.close()
                print(self.clients)
                break

    def send_message_to_all(self, message):
        """
        Notifies everyone new member entered the chat
        """
        for client in self.clients.keys():
            client.send(message.encode())

    def send_client(self, sock, message):
        sock.send(message.encode())
