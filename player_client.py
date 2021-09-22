import socket
import sys
import threading
import time

from constants import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
GAME_OVER = False

class PlayerClient:
    def __init__(self):
        nickname = input("Please specify your nickname:\n>> ")
        with sock as s:
            print(server_ip, server_port, "THE PORT")
            s.connect((server_ip, server_port))
            s.sendall(bytes(nickname, encoding='ascii'))
            data = s.recv(1024)
        self.nick = nickname
        self.deck, self.sets = ('Received', eval(repr(data)))


def message_thread():
    """
    This function handles messaging
    :return:
    """
    response, _ = sock.recvfrom(1024)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: client.py <server-ip> <port>")
        sys.exit()

    player = PlayerClient()
    print(f"Connected to server on IP: {server_ip}, PORT: {server_port}")
    while not GAME_OVER:
        time.sleep(1)




