import time

from client import Client
cl = Client()
cl.connect("yanir")
cl.set_msg("Hello")
cl.set_msg("World","yanir")
cl.get_list_file()
cl.get_users()
cl.download("test.txt")
time.sleep(10)
cl.download("test.txt")
cl.disconnect()