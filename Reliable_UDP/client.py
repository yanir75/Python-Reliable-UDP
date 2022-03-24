import os
from socket import *
from threading import *
#import logging


class Client:
    """
    Client class for the chat application.
    """

    def __init__(self, udp_port=50010, download_streams=2, DEBUG=False):

        # Creating and Configuring Logger

        """
        Initialize the client
        :param udp_port: Port start of the udp streams
        :param download_streams: amount of udp streams
        """
        self.activate = []
        self.deactivate = []
        # self.DEBUG = DEBUG
        # if DEBUG:
        #     logging.basicConfig(filename="client_logfile.log",
        #                         filemode='a',
        #                         format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        #                         datefmt='%H:%M:%S',
        #                         level=logging.INFO)
        #
        #     self.logger = logging.getLogger('Client')
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
        self.last_byte = 0
        # for tests
        self.last_msg = None

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
            # if self.DEBUG:
            #     self.logger.info(f'send <set_msg_all><{message}>!@#$')
        else:
            self.socket.send(f'<set_msg><{name}><{message}>!@#$'.encode())
            # if self.DEBUG:
            #     self.logger.info(f'send <set_msg><{name}><{message}>!@#$')

    def get_list_file(self):
        """
        Receive a list of downloadable files from the server
        """
        self.socket.send(f'<get_list_file>!@#$'.encode())
        # if self.DEBUG:
        #     self.logger.info(f'send <get_list_file>!@#$')

    def download(self, file_name):
        """
        Requests to download a file from the server
        """
        # if we are already downloading a file don't do anything
        # if delete count = 1 you are downloading the first half of the file
        # if delete count = 2 you are downloading the second half of the file
        # if delete count = 3 you finished and requested another file
        # however if delete count = 2 and you requested a new file we will delete the previous one

        # cannot download the same file twice immediately, if the files exists it will not download correctly
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
            # if self.DEBUG:
            #     self.logger.info(f'send <download><{file_name}>!@#$')
            self.file_name = file_name
        else:
            # self.logger.warning('Already downloading a file')
            for func in self.funcs:
                func("<Already downloading>")

    def download_file(self, file_name):
        self.downloading = True
        """
        Download the file from the server
        """
        for func in self.deactivate:
            func()
        # open the file for binary reading
        self.file = open(file_name, 'ab')
        # if self.DEBUG:
        #     self.logger.info(f'file opened for writing {file_name}')
        # self.threads.append(Thread(target=self.recv_and_send, args=(50010, 0)))
        # self.threads.append(Thread(target=self.recv_and_send, args=(50011, 0)))
        # for thread in self.threads:
        #     thread.start()
        # for thread in self.threads:
        threads = []
        # start the threads wait for the threads to finish
        for i in range(self.download_streams):
            threads.append(Thread(target=self.recv_and_send, args=(50010 + i,)))
        for i in range(self.download_streams - 1, -1, -1):
            threads[i].start()
        for i in range(self.download_streams):
            threads[i].join()

        # when all the threads are finished continue writing to the file
        while len(self.file_dict) != 0:
            # print(self.file_dict)
            self.write_to_file()
        for func in self.funcs:
            func(f'last byte received is {self.last_byte[-1]}')
        self.ind = 1
        self.file.close()
        self.file = None
        self.downloading = False
        if self.delete_count == 1:
            for func in self.funcs:
                func("Finished downloading half of the file, if you want to proceed enter the same file name and "
                     "press download again")
        elif self.delete_count == 2:
            for func in self.funcs:
                func("Finished downloading the file")
        for func in self.activate:
            func()

        # if self.DEBUG:
        #     self.logger.info(f'Finished downloading file {file_name}')

    def get_msg(self):
        """
        Get the messages from the server and handle them
        :return:
        """
        # While running get the messages from the server
        while self.running:
            # Receive the message from the server
            message = self.socket.recv(1024).decode()
            self.last_msg = message
            # if self.DEBUG:
            #     self.logger.info(f'received {message}')
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
        # received for double package
        received = {}
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(10)
        first_msg = True
        while first_msg:
            try:
                # send to the server to start downloading -99 flag
                sock.sendto(start.to_bytes(5, byteorder="big", signed=True), (address, port))
                msg, addr = sock.recvfrom(buffer_size)
                first_msg = False
                sock.settimeout(100)
            except Exception as e:
                # self.logger.error(e)
                # print("first try")
                pass
        while True:
            # print(f'{msg.decode()}')
            # write to file, since it is slower than receiving the file
            if self.ind % self.download_streams == port % self.download_streams and self.ind in self.file_dict.keys():
                self.write_to_file()
            # receive and handle the file
            value = msg
            # sequence number to send ACK
            seq = int.from_bytes(value[:5], byteorder='big', signed=True)
            # print(seq)
            # Done sequence number
            if seq == -100:
                # sock.sendto(seq.to_bytes(4, ), (address, port))
                break
            # if the sequence number is not in the dictionary add it to the dictionary and the data
            if seq not in received.keys():
                data = value[5:]
                self.lock.acquire()
                self.file_dict[seq] = data
                received[seq] = True
                self.lock.release()
            # send ACK
            sock.sendto(seq.to_bytes(5, byteorder='big', signed=True), (address, port))
            try:
                # receive the next message
                msg, addr = sock.recvfrom(buffer_size)
            except timeout:
                # self.logger.error("Timeout")
                # print("second timeout")
                pass

        sock.settimeout(5.0)
        while True:
            try:
                fin = -100
                sock.sendto(fin.to_bytes(5, byteorder='big', signed=True), (address, port))
                sock.recvfrom(buffer_size)
            except timeout:
                break

    def write_to_file(self):
        """
        Write the data to the file
        :return:
        """
        # print("writing to file")
        # print(self.file_dict[self.ind])
        self.file.write(self.file_dict[self.ind])
        self.last_byte = self.file_dict.pop(self.ind)
        self.ind += 1
