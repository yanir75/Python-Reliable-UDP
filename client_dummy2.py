import time

from client import *

cl = Client()
cl.connect("ron")
cl.set_msg("Hello World","yanir")
cl.disconnect()
