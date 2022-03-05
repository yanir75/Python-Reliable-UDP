import unittest
from server import Server
from client import Client
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
        self.assertTrue(filecmp.cmp('test.txt', './files/test.txt'))
        cl.download("elevator.png")
        time.sleep(8)
        cl.download("elevator.png")
        time.sleep(8)
        self.assertTrue(filecmp.cmp('elevator.png', 'elevator.png'))
        ser.disconnect_all()


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
        self.assertEqual('<---file_lst---><3><Elevator.png><no_shit.txt><test.txt><---end--->', cl.last_msg)
        time.sleep(0.2)
        ser.disconnect_all()


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