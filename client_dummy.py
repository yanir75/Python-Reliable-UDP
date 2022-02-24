from client import *

cl = Client()
cl.connect("yanir")
cl.download("test.txt")
time.sleep(10)
cl.download("test.txt")