import socket
from constants import *

class PlayerClient:
    def __init__(self):
        nickname = input("Please specify your nickname:\n>> ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(bytes(nickname, encoding='ascii'))
            data = s.recv(1024)

        self.nick, self.deck, self.sets = ('Received', eval(repr(data)))



