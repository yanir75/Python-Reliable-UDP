from client import *

cl = Client()
cl.connect("yanir")
cl.download("Elevator.png")
time.sleep(10)
cl.download("Elevator.png")