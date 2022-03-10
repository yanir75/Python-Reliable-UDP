import unittest
from TCP_UDP.server import Server
from TCP_UDP.client import Client
import time
from threading import *

class TestGetUsers(unittest.TestCase):
    def test_get_users(self):
        cl = Client()
        ser = Server()
        t1 = Thread(target=ser.run)
        t1.setDaemon(True)
        t1.start()
        time.sleep(0.2)
        cl.connect("test")
        cl.get_users()
        time.sleep(0.2)
        self.assertEqual('<get_users>', ser.last_msg)
        time.sleep(0.2)
        self.assertEqual('<---users_lst---><1><test><---end--->', cl.last_msg)
        time.sleep(0.2)
        ser.disconnect_all()