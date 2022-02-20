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
        self.download_file(file_name)

    def download_file(self, file_name):
        """
        To be continued
        """
        return False


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
