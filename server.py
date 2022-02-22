import os
from socket import *
from threading import *


class Server:
    def __init__(self):
        """
        Create a server and add the needed fields.
        """
        # AF_inet = IPv4 address family and SOCK_STREAM = TCP
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.stream1 = socket(AF_INET, SOCK_DGRAM)
        self.stream2 = socket(AF_INET, SOCK_DGRAM)
        self.available = True

        self.stream1_download = {}
        self.stream2_download = {}

        self.stream1_send = False
        self.stream2_send = False

        self.waiting_for_proceed = []
        self.download_queue = {}
        # bind the socket to the port number and host address (localhost) and listen for connections (5) at max,
        # at a time
        self.socket.bind(('127.0.0.1', 50002))
        self.socket.listen(5)
        # create a list of clients to store the clients connected to the server
        self.clients = {}
        self.window_size = 1

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
                    raise Exception("A client has disconnected")
                elif message == "<get_users>":
                    msg = f'<---users_lst---><{len(self.clients)}>'
                    for client in self.clients.values():
                        msg += f'<{client}>'
                    msg += '<---end--->'
                    self.send_client(sock, msg)
                elif message.startswith("<set_msg>"):
                    mess = message.split('<')
                    to = mess[2][:-1]
                    msg = mess[3][:-1]
                    for client in self.clients.keys():
                        if self.clients[client] == to:
                            self.send_client(client, f'<{name}:{msg}>')
                elif message.startswith("<set_msg_all>"):
                    self.send_message_to_all(f'<{name}:{message[14:-1]}>')
                elif message == "<get_list_file>":
                    file_list = os.listdir('./files')
                    msg = f'<---file_lst---><{len(file_list)}>'
                    for file in file_list:
                        msg += f'<{file}>'
                    msg += '<---end--->'
                    self.send_client(sock, msg)
                elif message.startswith("<download>"):
                    file_name = message[11:-1]
                    if not os.path.exists('./files/' + file_name):
                        self.send_client(sock, "<file_not_found>")




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

    def send_file_udp(self, stream, stream_send, curr_download, port, host="127.0.0.1"):
        window_size = 1
        time_out = 1
        stream.bind((host, port))
        first_msg = True
        while True:
            if first_msg:
                try:
                    data, addr = stream.recvfrom(1024)
                    first_msg = False
                except timeout:
                    continue
            else:
                i = 0
                for key in curr_download.keys():
                    if i == window_size:
                        break
                    i += 1
                    stream.sendto(curr_download[key].encode(), addr)
                i = 0
                while i < window_size:
                    stream.settimeout(time_out)
                    try:
                        data, addr = stream.recvfrom(5)
                        self.curr_download.pop(int(data.decode()))
                        i += 1
                    except timeout:
                        i += 1
            if len(curr_download.keys()) == 0 and not stream_send:
                first_msg = True

    def write_to_dict(self, file, file_name, name):
        size = os.path.getsize('./files/' + file_name)
        size = size / 1014 + 1
        byte = file.read(507)
        ind = 1
        if self.download_queue.get(name)[1] == 0:
            self.download_queue[name] = (file, 1)
            while byte and ind <= size:
                if ind % 2 == 0:
                    msg = self.ripud(ind)
                    self.stream1[ind] = msg + byte
                else:
                    msg1 = self.ripud(ind)
                    self.stream2[ind] = msg1 + byte
        else:
            self.download_queue.pop(name)
            while byte and ind <= size:
                if ind % 2 == 0:
                    msg = self.ripud(ind)
                    self.stream1[ind] = msg + byte
                else:
                    msg1 = self.ripud(ind)
                    self.stream2[ind] = msg1 + byte

    def ripud(self, ind):
        if ind < 10:
            return "0000" + str(ind)
        elif ind < 100:
            return "000" + str(ind)
        elif ind < 1000:
            return "00" + str(ind)
        elif ind < 10000:
            return "0" + str(ind)
        else:
            return str(ind)
