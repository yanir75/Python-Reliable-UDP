import unittest
from TCP_UDP.server import Server
from TCP_UDP.client import Client
import time
from threading import *

class TestFileList(unittest.TestCase):
    def test_file_list(self):
        cl = Client()
        ser = Server()
        t1 = Thread(target=ser.run)
        t1.setDaemon(True)
        t1.start()
        time.sleep(0.2)
        cl.connect("test")
        cl.get_list_file()
        time.sleep(0.2)
        self.assertEqual('<get_list_file>', ser.last_msg)
        time.sleep(0.2)
        self.assertEqual('<---file_lst---><2><Elevator.png><test.txt><---end--->', cl.last_msg)
        time.sleep(0.2)
        ser.disconnect_all()