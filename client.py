import threading
import time
from socket import *
from threading import *


class Client:
    def __init__(self):
        """
        Initialize the client.
        """
        self.running = True
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.funcs = []
        self.file_dict = {}
        self.packet_number = 0
        self.lock = Lock()
        self.threads = []
        self.ind = 0
        self.file = None

    def connect(self, name, host='127.0.0.1', port=50002):
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
        self.socket.send(f'<download><{file_name}>'.encode())
        time.sleep(0.1)

    def download_file(self, file_name):
        """
        To be continued
        """
        self.file = open(file_name, 'wb')
        self.threads.append(Thread(target=self.recv_and_send, args=(50010, 0)))
        self.threads.append(Thread(target=self.recv_and_send, args=(50011, 0)))
        for thread in self.threads:
            thread.start()

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
            if message == '<middle>':
                for thread in self.threads:
                    thread.wait()
            if message == '<proceeded>':
                for thread in self.threads:
                    thread.notify()

    def proceed(self):
        self.socket.send(f'<proceed>'.encode())

    def recv_and_send(self, port, start, address="127.0.0.1", buffer_size=1024):
        """
        Receive the file from the server
        """
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(1.0)
        first_msg = True
        while True:
            if first_msg:
                try:
                    sock.sendto(f'{start}', (address, port))
                    msg = sock.recvfrom(buffer_size)
                    first_msg = False
                    sock.settimeout(100)
                except Exception as e:
                    print(e)
            else:
                if self.ind % 2 == start % 2 and self.ind in self.file_dict.keys():
                    self.write_to_file()
                value = msg[0].decode()
                seq = value[:5]
                if seq == 'DONE!':
                    sock.sendto(f'DONE!', (address, port))
                    break
                seq = int(seq)
                data = value[5:]
                self.lock.acquire()
                self.file_dict[seq] = data
                self.lock.release()
                sock.send(f'{seq}'.encode())
                msg = sock.recvfrom(buffer_size)

        sock.settimeout(5.0)
        while True:
            try:
                sock.recvfrom(buffer_size)
                break
            except:
                sock.sendto(f'DONE!', (address, port))

    def write_to_file(self, file):
        file.write(self.file_dict[self.ind].encode("ascii"))
        self.file_dict.pop(self.ind)
        self.ind += 1
