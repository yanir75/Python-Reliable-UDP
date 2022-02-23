from client import *

cl = Client()
cl.connect("yanir")
cl.download("test.txt")
time.sleep(5)
cl.download("no_shit.txt")