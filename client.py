import os
import time
from socket import *
from threading import *


# TODO: add comments

class Client:
    def __init__(self, udp_port=50010, download_streams=2):
        """
        Initialize the client.
        """
        self.file_name = ""
        self.running = True
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.funcs = []
        self.file_dict = {}
        self.packet_number = 0
        self.lock = Lock()
        self.threads = []
        self.ind = 1
        self.file = None
        self.downloading = False
        self.delete_count = 0
        self.download_streams = download_streams
        self.udp_port = udp_port

    def connect(self, name, host='127.0.0.1', port=50000):
        """
        Connect to the server
        """
        # Connect to the server and send the name of the client
        self.socket.connect((host, port))
        connect_message = f'<connect><{name}>'
        self.socket.send(connect_message.encode())
        time.sleep(0.1)
        Thread(target=self.get_msg).start()

    def get_users(self):
        """
        Get the list of connected users from the server
        """
        # Get the list of users from the server
        self.socket.send(f'<get_users>'.encode())
        time.sleep(0.1)

    def disconnect(self):
        """
        Disconnect from the server
        """
        self.socket.send(f'<disconnect>'.encode())

    def set_msg(self, message, name='all'):
        """
        Send a message to a specific client
        """
        if name == 'all':
            self.socket.send(f'<set_msg_all><{message}>'.encode())
            time.sleep(0.1)
        else:
            self.socket.send(f'<set_msg><{name}><{message}>'.encode())
            time.sleep(0.1)

    def get_list_file(self):
        """
        Receive a list of downloadable files from the server
        """
        self.socket.send(f'<get_list_file>'.encode())
        time.sleep(0.1)

    def download(self, file_name):
        """
        Requests to download a file from the server
        """
        if not self.downloading:
            self.delete_count += 1
            if self.file_name != file_name and self.delete_count == 3:
                self.delete_count = 1
            if self.file_name != file_name and self.delete_count == 2:
                # delete file if it exists
                if os.path.exists(self.file_name):
                    os.remove(self.file_name)
                self.delete_count = 1
            self.socket.send(f'<download><{file_name}>'.encode())
            self.file_name = file_name
            time.sleep(0.1)
        else:
            print("You are in a middle wait you piece of shit")

    def download_file(self, file_name):
        self.downloading = True
        """
        To be continued
        """
        self.file = open(file_name, 'ab')
        # self.threads.append(Thread(target=self.recv_and_send, args=(50010, 0)))
        # self.threads.append(Thread(target=self.recv_and_send, args=(50011, 0)))
        # for thread in self.threads:
        #     thread.start()
        threads = []
        for i in range(self.download_streams):
            threads.append(Thread(target=self.recv_and_send, args=(50010 + i, -i)))
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
            print(self.file_dict)
            self.write_to_file()
        self.ind = 1
        self.file.close()
        self.file = None
        self.downloading = False

    def get_msg(self):
        """
        Get the messages from the server
        """
        while self.running:
            # Receive the message from the server
            message = self.socket.recv(1024).decode()
            print(message)
            # activate the functions on each message
            for func in self.funcs:
                func(message)
            if message == '<disconnected>':
                self.socket.close()
                self.running = False
            if message == '<start>':
                Thread(target=self.download_file, args=(self.file_name,)).start()

    def recv_and_send(self, port, start, address="127.0.0.1", buffer_size=512):
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
                sock.sendto(f'{start}'.encode(), (address, port))
                msg, addr = sock.recvfrom(buffer_size)
                first_msg = False
                sock.settimeout(100)
            except Exception as e:
                print(e)
        while True:

            # print(f'{msg.decode()}')
            if self.ind % self.download_streams == start % self.download_streams and self.ind in self.file_dict.keys():
                self.write_to_file()
            value = msg
            seq = value[:5].decode()
            if seq == 'DONE!':
                # sock.sendto(f'DONE!'.encode(), (address, port))
                break
            seq = int(seq)
            if seq not in received.keys():
                data = value[5:]
                self.lock.acquire()
                self.file_dict[seq] = data
                received[seq] = True
                self.lock.release()
            sock.sendto(f'{seq}'.encode(), (address, port))
            msg, addr = sock.recvfrom(buffer_size)

        sock.settimeout(5.0)
        while True:
            try:
                sock.sendto(f'DONE!'.encode(), (address, port))
                sock.recvfrom(buffer_size)
            except timeout:
                break

    def write_to_file(self):
        print("writing to file")
        print(self.file_dict[self.ind])
        self.file.write(self.file_dict[self.ind])
        self.file_dict.pop(self.ind)
        self.ind += 1
