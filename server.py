import os
from socket import *
from threading import *


class Server:
    def __init__(self, address="127.0.0.1", tcp_port=50000, udp_port=50010, num_of_streams=2):
        """
        Create a server and add the needed fields.
        """
        # AF_inet = IPv4 address family and SOCK_STREAM = TCP
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.streams = []
        self.available = []
        self.streams_send = []
        self.udp_port = udp_port
        self.num_of_streams = num_of_streams
        self.streams_download = []
        for _ in range(self.num_of_streams):
            self.available.append(True)
            self.streams_send.append(True)
            self.streams.append(socket(AF_INET, SOCK_DGRAM))
            self.streams_download.append({})
        self.lock = Lock()
        self.address = address
        self.waiting_for_proceed = []
        self.download_queue = {}
        print(self.streams_download)
        # bind the socket to the port number and host address (localhost) and listen for connections (5) at max,
        # at a time
        self.socket.bind((self.address, tcp_port))
        self.socket.listen(5)
        # create a list of clients to store the clients connected to the server
        self.clients = {}
        self.window_size = 1

    def run(self,packet_size=1024):
        """
        Run the server and listen for connections.
        """
        for i in range(self.num_of_streams):
            Thread(target=self.send_file_udp,
                   args=(self.streams[i], self.streams_download[i], self.udp_port + i)).start()
        while True:
            # accept a connection from a client
            sock, addr = self.socket.accept()
            # receive the name of the client
            name = sock.recv(packet_size).decode()
            name = name[10:-1]
            # add the client to the list of clients
            self.send_message_to_all("A new member has entered the chat: " + name)
            self.send_client(sock, "<connected>")
            self.clients[sock] = name
            # create a thread to handle the client
            Thread(target=self.handle_client, args=(sock, name)).start()

    def handle_client(self, sock, name, packet_size=1024):
        """
        Handle the client and listen for his commands
        """
        while True:
            try:
                # receive the message from the client
                message = sock.recv(packet_size).decode()
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
                        boolen = True
                        for i in range(self.num_of_streams):
                            if not self.available[i]:
                                boolen = False
                        if boolen:
                            self.send_client(sock, f'<start>')
                            if name not in self.download_queue.keys():
                                file = open('./files/' + file_name, 'rb')
                                self.download_queue[name] = (file, file_name)
                                Thread(target=self.write_to_dict, args=(file, False, file_name)).start()
                            else:
                                if file_name != self.download_queue[name][1]:
                                    file = self.download_queue[name][0]
                                    file.close()
                                    file = open('./files/' + file_name, 'r')
                                    self.download_queue[name] = (file, file_name)
                                Thread(target=self.write_to_dict,
                                       args=(self.download_queue[name][0], True, file_name)).start()
                                self.download_queue.pop(name)
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

    def send_file_udp(self, stream, curr_download, port):
        window_size = 1
        time_out = 10
        stream.bind((self.address, port))
        first_msg = True
        print(port)
        while True:
            if first_msg is True:
                try:
                    data, addr = stream.recvfrom(1024)
                    print(data.decode())
                    first_msg = False
                    print("test")
                    print(curr_download)
                except timeout:
                    print("time____out")
            else:
                i = 0
                # synchronize the stream
                self.lock.acquire()
                for key in curr_download.keys():
                    if i == window_size:
                        break
                    i += 1
                    stream.sendto(curr_download[key], addr)
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
            while len(curr_download.keys()) == 0 and not self.streams_send[port % self.num_of_streams]:
                first_msg = True
                try:
                    stream.settimeout(1)
                    stream.sendto("DONE!".encode(), addr)
                    data, addr = stream.recvfrom(1024)
                    if data.decode() != "DONE!":
                        raise timeout
                    self.streams_send[port % self.num_of_streams] = True
                    self.available[port % self.num_of_streams] = True
                except timeout:
                    print("timeout")

    def write_to_dict(self, file, close_file, file_name,packet_size=507):
        print("started")
        for i in range(self.num_of_streams):
            self.streams_send[i] = True
        num_of_packets = os.path.getsize('./files/' + file_name)
        num_of_packets = num_of_packets / (packet_size*2) + 1
        byte = file.read(packet_size)
        ind = 1
        while byte:
            self.lock.acquire()
            key = self.ripud(ind)
            msg = key.encode()
            msg += byte
            self.streams_download[ind % self.num_of_streams][int(key)] = msg
            ind += 1
            if ind <= num_of_packets:
                byte = file.read(packet_size)
            else:
                self.lock.release()
                break
            self.lock.release()
        if close_file:
            file.close()
        for i in range(self.num_of_streams):
            self.streams_send[i] = False

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
