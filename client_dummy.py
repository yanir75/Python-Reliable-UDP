from client import *

cl = Client()
cl.connect("yanir")
cl.download("test.txt")
time.sleep(30)
cl.download("test.txt")