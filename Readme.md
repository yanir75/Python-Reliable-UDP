# Python Reliable udp
In this project we created a chat with the option to download a file.  
The chat was implemented in TCP,File downloading however was implemented in UDP. But we had to make it reliable, we wouldn't want to miss part of the file. 

--------------

# Implementation
Chat was implemented through sending TCP messages to the server, the server will transfer the message to whomever needed.  
A convention of messages was implemented to our GUIs. Thus the server can seperate and operate on each message.  
We decided to implement few UDP streams (can be decided on creating the objects). Which will transfer the file simultaneously to the client.  
The client will receive the file and reconstruct it on his side.  
In this implementation we tried to simulate Quic over regular (not http or https) communication.


--------------

# Structure
Classes we used to implement the project.
![UML](https://raw.githubusercontent.com/yanir75/Python-TCP-Over-UDP/main/UML/Structure_uml.jpg)


--------------

# How to use
Clone the repository
```
git clone https://github.com/yanir75/Python-Reliable-UDP.git && cd Python-Reliable-UDP/Reliable_UDP
```

In case you don't have tkinter module
```
sudo apt-get install python3-tk
```

Run the server gui
```
python server_gui.py
```

Activate the server then you can activate up to 5 clients.  
Run the client
```
python client_gui.py
```


--------------
# Sources
  - <a href="https://www.cs.princeton.edu/courses/archive/fall16/cos561/papers/Cubic08.pdf">Princeton cubic research</a>
  - <a href="https://en.wikipedia.org/wiki/QUIC">QUIC information</a>
