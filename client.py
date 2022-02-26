import os
from socket import *
from threading import *


class Client:
    """
    Client class for the chat application.
    """

    def __init__(self, udp_port=50010, download_streams=2):
        """
        Initialize the client
        :param udp_port: Port start of the udp streams
        :param download_streams: amount of udp streams
        """
        # File name
        self.file_name = ""
        # running flag
        self.running = True
        # downloading flag
        self.socket = socket(AF_INET, SOCK_STREAM)
        # functions to activate on the message we receive
        self.funcs = []
        # file dictionary
        self.file_dict = {}
        # global lock
        self.lock = Lock()
        # amount of udp threads
        self.threads = []
        # index for the sequence number
        self.ind = 1
        # the file pointer
        self.file = None
        # downloading flag
        self.downloading = False
        # delete count wether to delete the file or not
        self.delete_count = 0
        # amount of download streams
        self.download_streams = download_streams
        self.udp_port = udp_port

    def connect(self, name, host='127.0.0.1', port=50000):
        """
        Connect to the server
        <connect><name>!@#$
        :param name:
        :param host:
        :param port:
        :return:
        """
        # Connect to the server and send the name of the client
        self.socket.connect((host, port))
        connect_message = f'<connect><{name}>!@#$'
        self.socket.send(connect_message.encode())
        Thread(target=self.get_msg).start()

    def get_users(self):
        """
        Get the list of users from the server
        :return:
        """
        # Get the list of users from the server
        self.socket.send(f'<get_users>!@#$'.encode())

    def disconnect(self):
        """
        Disconnect from the server
        """
        self.socket.send(f'<disconnect>!@#$'.encode())

    def set_msg(self, message, name='all'):
        """
        Send a message to a specific client
        """
        if name == 'all':
            self.socket.send(f'<set_msg_all><{message}>!@#$'.encode())
        else:
            self.socket.send(f'<set_msg><{name}><{message}>!@#$'.encode())

    def get_list_file(self):
        """
        Receive a list of downloadable files from the server
        """
        self.socket.send(f'<get_list_file>!@#$'.encode())

    def download(self, file_name):
        """
        Requests to download a file from the server
        """
        # if we are already downloading a file don't do anything
        #
        if not self.downloading:
            self.delete_count += 1
            if self.file_name != file_name and self.delete_count == 3:
                self.delete_count = 1
            if self.file_name != file_name and self.delete_count == 2:
                # delete file if it exists
                if os.path.exists(self.file_name):
                    os.remove(self.file_name)
                self.delete_count = 1
            self.socket.send(f'<download><{file_name}>!@#$'.encode())
            self.file_name = file_name
        else:
            for func in self.funcs:
                func("You are in a middle wait you piece of shit")

    def download_file(self, file_name):
        self.downloading = True
        """
        Download the file from the server
        """
        self.file = open(file_name, 'ab')
        # self.threads.append(Thread(target=self.recv_and_send, args=(50010, 0)))
        # self.threads.append(Thread(target=self.recv_and_send, args=(50011, 0)))
        # for thread in self.threads:
        #     thread.start()
        threads = []
        for i in range(self.download_streams):
            threads.append(Thread(target=self.recv_and_send, args=(50010 + i,)))
        for i in range(self.download_streams - 1, -1, -1):
            threads[i].start()
        for i in range(self.download_streams):
            threads[i].join()

        # t2 = Thread(target=self.recv_and_send, args=(50011, -1))
        # t2.start()
        # t1.start()
        # t1.join()
        # t2.join()
        while len(self.file_dict) != 0:
            # print(self.file_dict)
            self.write_to_file()
        self.ind = 1
        self.file.close()
        self.file = None
        self.downloading = False

    def get_msg(self):
        """
        Get the messages from the server and handle them
        :return:
        """
        # While running get the messages from the server
        while self.running:
            # Receive the message from the server
            message = self.socket.recv(1024).decode()
            # print(message)
            # activate the functions on each message
            for func in self.funcs:
                func(message)
            # Disconnect from the server
            if message == '<disconnected>':
                self.socket.close()
                self.running = False
            # Start downloading the file
            if message == '<start>':
                Thread(target=self.download_file, args=(self.file_name,)).start()

    def recv_and_send(self, port, start=-99, address="127.0.0.1", buffer_size=512):
        """
        Receive the file from the server
        """
        # TODO: modify timeout
        received = {}
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(10)
        first_msg = True
        while first_msg:
            try:
                sock.sendto(start.to_bytes(5, byteorder="big", signed=True), (address, port))
                msg, addr = sock.recvfrom(buffer_size)
                first_msg = False
                sock.settimeout(100)
            except Exception as e:
                print(e)
        while True:
            # print(f'{msg.decode()}')
            if self.ind % self.download_streams == port % self.download_streams and self.ind in self.file_dict.keys():
                self.write_to_file()
            value = msg
            seq = int.from_bytes(value[:5], byteorder='big', signed=True)
            # print(seq)
            if seq == -100:
                # sock.sendto(seq.to_bytes(4, ), (address, port))
                break
            if seq not in received.keys():
                data = value[5:]
                self.lock.acquire()
                self.file_dict[seq] = data
                received[seq] = True
                self.lock.release()
            sock.sendto(seq.to_bytes(5, byteorder='big', signed=True), (address, port))
            try:
                msg, addr = sock.recvfrom(buffer_size)
            except timeout:
                print("timeout")

        sock.settimeout(5.0)
        while True:
            try:
                fin = -100
                sock.sendto(fin.to_bytes(5, byteorder='big', signed=True), (address, port))
                sock.recvfrom(buffer_size)
            except timeout:
                break

    def write_to_file(self):
        # print("writing to file")
        # print(self.file_dict[self.ind])
        self.file.write(self.file_dict[self.ind])
        self.file_dict.pop(self.ind)
        self.ind += 1
