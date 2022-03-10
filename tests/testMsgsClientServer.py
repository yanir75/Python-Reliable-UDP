import unittest
from TCP_UDP.server import Server
from TCP_UDP.client import Client
import time
from threading import *

class TestMsgs(unittest.TestCase):
    def test_msgs_client_server(self):
        cl = Client()
        ser = Server()
        t1 = Thread(target=ser.run)
        t1.setDaemon(True)
        t1.start()
        time.sleep(0.2)
        cl.connect("test")
        cl.set_msg("hello world")
        time.sleep(0.2)
        self.assertEqual('<set_msg_all><hello world>', ser.last_msg)
        time.sleep(0.2)
        self.assertEqual('<test: hello world>', cl.last_msg)
        time.sleep(0.2)
        cl.set_msg("hello world", 'test')
        time.sleep(0.2)
        self.assertEqual('<set_msg><test><hello world>', ser.last_msg)
        time.sleep(0.2)
        self.assertEqual('<test(private): hello world>', cl.last_msg)
        time.sleep(0.2)
        cl.download('file.txt')
        time.sleep(0.2)
        self.assertEqual('<download><file.txt>', ser.last_msg)
        time.sleep(0.2)
        self.assertEqual('<file not found>', cl.last_msg)
        time.sleep(0.2)
        ser.disconnect_all()
