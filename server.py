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
        self.available = [True, True]
        self.streams_send = [True, True]
        self.lock = Lock()

        self.stream1_download = {}
        self.stream2_download = {}

        self.waiting_for_proceed = []
        self.download_queue = {}
        # bind the socket to the port number and host address (localhost) and listen for connections (5) at max,
        # at a time
        self.socket.bind(('127.0.0.1', 50000))
        self.socket.listen(5)
        # create a list of clients to store the clients connected to the server
        self.clients = {}
        self.window_size = 1

    def run(self):
        """
        Run the server and listen for connections.
        """
        Thread(target=self.send_file_udp, args=(self.stream1, self.stream1_download, 50010)).start()
        Thread(target=self.send_file_udp, args=(self.stream2, self.stream2_download, 50011)).start()
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
                    else:
                        if self.available[0] and self.available[1]:
                            self.available[0] = False
                            self.available[1] = False
                            self.send_client(sock, f'<start>')
                            file = open('./files/' + file_name, 'r')
                            self.download_queue[name] = file
                            Thread(target=self.write_to_dict, args=(file, 0, 0)).start()
                        else:
                            self.send_client(sock, "<download_not_available>")





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

    def send_file_udp(self, stream, curr_download, port, host="127.0.0.1"):
        window_size = 1
        time_out = 10
        stream.bind((host, port))
        first_msg = True
        while True:
            if first_msg is True:
                try:
                    data, addr = stream.recvfrom(1024)
                    print(data.decode())
                    first_msg = False
                    print("test")
                    print(curr_download)
                except timeout:
                    print("timeout")
            else:
                i = 0
                # synchronize the stream
                self.lock.acquire()
                for key in curr_download.keys():
                    if i == window_size:
                        break
                    i += 1
                    stream.sendto(curr_download[key].encode(), addr)
                    print("send")
                self.lock.release()
                j = 0
                while j < i:
                    stream.settimeout(time_out)
                    try:
                        data, addr = stream.recvfrom(5)
                        curr_download.pop(int(data.decode()))
                        j += 1
                    except timeout:
                        j += 1
            while len(curr_download.keys()) == 0 and not self.streams_send[port % 2]:
                first_msg = True
                try:
                    stream.settimeout(1)
                    stream.sendto("DONE!".encode(), addr)
                    data, addr = stream.recvfrom(1024)
                    self.streams_send[port % 2] = True
                    self.available[port % 2] = True
                except timeout:
                    print("timeout")

    def write_to_dict(self, file, file_name, name):
        print("started")
        self.streams_send = True
        # size = os.path.getsize('./files/' + file_name)
        # size = size / 1014 + 1
        byte = file.read(507)
        ind = 1
        # if self.download_queue.get(name)[1] == 0:
        #     self.download_queue[name] = (file, 1)
        #     while byte and ind <= size:
        #         if ind % 2 == 0:
        #             msg = self.ripud(ind)
        #             self.stream1[ind] = msg + byte
        #         else:
        #             msg1 = self.ripud(ind)
        #             self.stream2[ind] = msg1 + byte
        # else:
        #     self.download_queue.pop(name)
        #     while byte:
        #         if ind % 2 == 0:
        #             msg = self.ripud(ind)
        #             self.stream1[ind] = msg + byte
        #         else:
        #             msg1 = self.ripud(ind)
        #             self.stream2[ind] = msg1 + byte
        while byte:
            self.lock.acquire()
            if ind % 2 == 0:
                msg = self.ripud(ind)
                msg += byte
                self.stream1_download[ind] = msg
                byte = file.read(507)
            else:
                msg1 = self.ripud(ind)
                msg1 += byte
                self.stream2_download[ind] = msg1
                byte = file.read(507)
            self.lock.release()
            ind += 1
        file.close()
        self.streams_send = [False,False]

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
