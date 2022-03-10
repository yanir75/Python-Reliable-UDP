import unittest
from TCP_UDP.server import Server
from TCP_UDP.client import Client
import time
from threading import *

class TestMsgsBetweenUsers(unittest.TestCase):
    def test_msgs_between_users(self):
        cl = Client()
        cl2 = Client()
        ser = Server()
        t1 = Thread(target=ser.run)
        t1.setDaemon(True)
        t1.start()
        time.sleep(0.2)
        cl.connect("test")
        cl2.connect("check")
        time.sleep(0.2)
        cl2.set_msg("hello test", "test")
        time.sleep(0.2)
        self.assertEqual('<check(private): hello test>', cl.last_msg)
        time.sleep(0.2)
        cl.set_msg("hello check", "check")
        time.sleep(0.2)
        self.assertEqual('<test(private): hello check>', cl2.last_msg)
        cl3 = Client()
        cl3.connect("last one")
        time.sleep(0.2)
        cl3.set_msg("hello all")
        time.sleep(0.2)
        self.assertEqual('<last one: hello all>', cl2.last_msg)
        self.assertEqual('<last one: hello all>', cl.last_msg)
        self.assertEqual('<last one: hello all>', cl3.last_msg)
        ser.disconnect_all()
