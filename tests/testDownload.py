import unittest
from TCP_UDP.server import Server
from TCP_UDP.client import Client
import time
import filecmp
from threading import *


class TestDownload(unittest.TestCase):
    def test_file_download(self):
        cl = Client()
        ser = Server()
        t1 = Thread(target=ser.run)
        t1.setDaemon(True)
        t1.start()
        time.sleep(2)
        cl.connect("test")
        time.sleep(2)
        cl.download("test.txt")
        time.sleep(8)
        cl.download("test.txt")
        time.sleep(8)
        self.assertTrue(filecmp.cmp('test.txt', '../files/test.txt'))
        cl.download("elevator.png")
        time.sleep(8)
        cl.download("elevator.png")
        time.sleep(8)
        self.assertTrue(filecmp.cmp('elevator.png', 'elevator.png'))
        ser.disconnect_all()