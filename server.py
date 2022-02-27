import os
from socket import *
from threading import *


# import sched, time

class Server:

    def __init__(self, address="127.0.0.1", tcp_port=50000, udp_port=50010, num_of_streams=2):
        """
        Initialize the server.
        :param address: Server address
        :param tcp_port: TCP socket port
        :param udp_port: UDP socket ports
        :param num_of_streams: Number of UDP parallel streams
        """
        self.disable = []
        # AF_inet = IPv4 address family and SOCK_STREAM = TCP
        self.socket = socket(AF_INET, SOCK_STREAM)
        # UDP streams (sockets) list
        self.streams = []
        # UDP availability to download list
        self.available = []
        # Is the UDP stream transmitting
        self.streams_send = []
        self.funcs = []

        # self explanatory
        self.udp_port = udp_port
        self.num_of_streams = num_of_streams
        # file dicts for streams to send
        self.streams_download = []
        for _ in range(self.num_of_streams):
            self.available.append(True)
            self.streams_send.append(True)
            self.streams.append(socket(AF_INET, SOCK_DGRAM))
            self.streams_download.append({})
        # global locks
        self.lock = Lock()
        self.address = address
        # download queue (only one can download)
        self.download_queue = {}
        # bind the socket to the port number and host address (localhost) and listen for connections (5) at max,
        # at a time
        self.socket.bind((self.address, tcp_port))
        self.socket.listen(5)
        # create a list of clients to store the clients connected to the server
        self.clients = {}
        self.window_size = 5

    def run(self, packet_size=1024):
        """
        Run the server.
        :param packet_size: to receive at a time
        :return:
        """
        for i in self.disable:
            i()
        # run the UDP streams to listen to file downloads
        for i in range(self.num_of_streams):
            Thread(target=self.send_file_udp,
                   args=(self.streams[i], self.streams_download[i], self.udp_port + i)).start()
        while True:
            # accept a connection from a client
            sock, addr = self.socket.accept()
            # receive the name of the client
            name = sock.recv(packet_size).decode()
            name = name[10:-5]
            # print(name)
            # add the client to the list of clients
            self.send_message_to_all("A new member has entered the chat: " + name)
            for func in self.funcs:
                func("A new member has entered the chat: " + name)
            self.send_client(sock, "<connected>")
            self.clients[sock] = name
            # create a thread to handle the client
            Thread(target=self.handle_client, args=(sock, name)).start()

    def handle_client(self, sock, name, packet_size=1024):
        """
        Handle the client.
        :param sock: The client socket
        :param name: The name of the client
        :param packet_size: Size of the receiving packet
        :return:
        """
        while True:
            try:
                # receive the message from the client
                messages = sock.recv(packet_size).decode()
                msgs = messages.split("!@#$")
                # print(msgs)
                # handle the message
                for message in msgs[:-1]:
                    for func in self.funcs:
                        func(f'{name}: {message}')
                    #    print(message)
                    # disconnect the client
                    if message == "<disconnect>":
                        self.send_client(sock, "<disconnected>")
                        raise Exception("A client has disconnected")
                    # Send the users to the client
                    elif message == "<get_users>":
                        msg = f'<---users_lst---><{len(self.clients)}>'
                        for client in self.clients.values():
                            msg += f'<{client}>'
                        msg += '<---end--->'
                        self.send_client(sock, msg)
                    # Send a private message
                    elif message.startswith("<set_msg>"):
                        mess = message.split('<')
                        to = mess[2][:-1]
                        msg = mess[3][:-1]
                        for client in self.clients.keys():
                            if self.clients[client] == to:
                                self.send_client(client, f'<{name}:{msg}>')
                    # send a public message
                    elif message.startswith("<set_msg_all>"):
                        #    print(message[14:-1])
                        self.send_message_to_all(f'<{name}:{message[14:-1]}>')
                    # send file list, (all the files in the folder named files)
                    elif message == "<get_list_file>":
                        file_list = os.listdir('./files')
                        msg = f'<---file_lst---><{len(file_list)}>'
                        for file in file_list:
                            msg += f'<{file}>'
                        msg += '<---end--->'
                        self.send_client(sock, msg)
                    # request for file download
                    elif message.startswith("<download>"):
                        file_name = message[11:-1]
                        # check if the file exists
                        if not os.path.exists('./files/' + file_name):
                            self.send_client(sock, "<file_not_found>")
                        # check availability of the socket
                        else:
                            boolen = True
                            for i in range(self.num_of_streams):
                                if not self.available[i]:
                                    boolen = False
                            # if all the streams are available for download start downloading
                            if boolen:
                                # send the client start
                                self.send_client(sock, f'<start>')
                                # if the name requested to download before that means he is at proceed
                                # if he is in proceed it will continue from where it stopped reading the file
                                # if he requests to download a new file and didn't press proceed it will start from the beginning
                                # this will forget the previous file and close it
                                # this will activate a thread to write the file into a private streams dictionary
                                if name not in self.download_queue.keys():
                                    file = open('./files/' + file_name, 'rb')
                                    self.download_queue[name] = (file, file_name)
                                    Thread(target=self.write_to_dict, args=(file, False, file_name)).start()
                                elif file_name != self.download_queue[name][1]:
                                    file = self.download_queue[name][0]
                                    file.close()
                                    file = open('./files/' + file_name, 'rb')
                                    self.download_queue[name] = (file, file_name)
                                    Thread(target=self.write_to_dict, args=(file, False, file_name)).start()
                                else:
                                    Thread(target=self.write_to_dict,
                                           args=(self.download_queue[name][0], True, file_name)).start()
                                    self.download_queue.pop(name)
                            else:
                                self.send_client(sock, "<download_not_available>")
            # in case of error pop the client and close the connection
            except Exception as e:
                # print(e)
                self.clients.pop(sock)
                sock.close()
                # print(self.clients)
                break
    def send_message_to_all(self, message):
        """
        send a message to all the clients
        :param message:
        :return:
        """
        # print(message)
        for client in self.clients.keys():
            client.send(message.encode())

    def send_client(self, sock, message):
        """
        Send message to a specific client
        :param sock:
        :param message:
        :return:
        """
        sock.send(message.encode())

    def send_file_udp(self, stream, curr_download, port):
        """
        Send the file to the client using reliable udp
        Our method is each stream will have a private dictionary to send.
        There is an additional thread writing to all the streams dictionaries.
        Each stream will have a separate port and will send the file to the matching stream in the client
        We chose selective repeat method for the udp
        We will use cubic congestion and flow control
        There are 5 bytes allocated to the sequence number (40 bits) we use the binary sequence number
        The file is being sent through binary reading meaning any file can be sent, but no directory
        :param stream:
        :param curr_download: file dict which write_to_dict will write to
        :param port:
        :return:
        """
        # window size
        window_size = 1
        # time_out
        time_out = 1000
        stream.bind((self.address, port))
        first_msg = True
        #print(port)
        # s = sched.scheduler(time.time, time.sleep)
        while True:
            if first_msg is True:
                # first message is the request to download -99 meaning start sending the file
                try:
                    stream.settimeout(time_out) # to take the time we do not expect many messages here
                    data, addr = stream.recvfrom(1024)
                    if int.from_bytes(data, byteorder='big', signed=True) == -99:
                        first_msg = False
                        time_out = 1
                        stream.settimeout(time_out) # we start sending the file
                    # print("test")
                    # print(curr_download)
                except timeout:
                    print("time____out")
            else:
                # index for the number of packets we sent to the client
                i = 0
                # synchronize the stream
                self.lock.acquire()
                # send the file through the stream until the window size is reached or we sent the whole file
                for key in curr_download.keys():
                    if i == window_size:
                        break
                    i += 1
                    # s.enter(i/10000, 1,  stream.sendto, (curr_download[key],addr))
                    stream.sendto(curr_download[key], addr)
                self.lock.release()
                # s.run()
                # index for the number packet we expect to receive from the client
                j = 0
                # TODO: modify window size and timeout
                # we expect to receive j ACKS from the client
                while j < i:
                    stream.settimeout(time_out)
                    try:
                        data, addr = stream.recvfrom(5)
                        index = int.from_bytes(data, byteorder='big', signed=True)
                        curr_download.pop(index)
                        j += 1
                    # timeout error
                    except timeout:
                        j += 1
                    # double ack error
                    except KeyError:
                        j += 1
            # verify that the client knows we are done sending the file
            while len(curr_download.keys()) == 0 and not self.streams_send[port % self.num_of_streams]:
                first_msg = True
                try:
                    # we expect to receive a message from the client within the same time_out
                    # -100 means we are done sending the file
                    stream.settimeout(time_out)
                    fin = -100
                    stream.sendto(fin.to_bytes(5, byteorder="big", signed=True), addr)
                    data, addr = stream.recvfrom(1024)
                    if int.from_bytes(data, byteorder="big", signed=True) != -100:
                        raise timeout
                    self.streams_send[port % self.num_of_streams] = True
                    self.available[port % self.num_of_streams] = True
                except timeout:
                    print("timeout")

    def write_to_dict(self, file, close_file, file_name, packet_size=507):
        """
        write to the dictionary which will be sent to the client
        :param file: File pointer
        :param close_file: Flag if to close the file
        :param file_name: the name of the file
        :param packet_size: packet_size to divide the file into packets
        :return:
        """
        #print("started")
        # change the streams to occupied
        for i in range(self.num_of_streams):
            self.streams_send[i] = True
        # get the file size
        num_of_packets = os.path.getsize('./files/' + file_name)
        # stop at the middle of the file / end if it is the second time
        num_of_packets = num_of_packets / (packet_size * 2) + 1
        byte = file.read(packet_size)
        # ind for the sequence number
        ind = 1
        # start reading the file and writing to all the streams dictionary
        while byte:
            # change the key to binary 5 bytes
            key = ind.to_bytes(5, byteorder='big', signed=True)
            msg = key + byte
            self.lock.acquire()
            # write the file to the dictionaries of the streams
            self.streams_download[ind % self.num_of_streams][ind] = msg
            self.lock.release()
            ind += 1
            # if we reached the end of the file/middle of the file we want to stop reading
            if ind <= num_of_packets:
                byte = file.read(packet_size)
            else:
                break
        # close the file according to the flag
        if close_file:
            file.close()
        # change the streams to not sending, meaning we are done editing their dictionary
        for i in range(self.num_of_streams):
            self.streams_send[i] = False
