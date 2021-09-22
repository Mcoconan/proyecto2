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

        print(server_ip, server_port, "THE PORT")
        sock.connect((server_ip, server_port))
        sock.sendall(bytes(nickname, encoding='ascii'))
        data = sock.recv(1024)
        self.nick = nickname
        self.deck, self.sets = ('Received', eval(repr(data)))


def game_thread():
    """
    This function handles messaging
    :return:
    """
    while not GAME_OVER:
        response, _ = sock.recvfrom(BUFF_SIZE)
        response = response.decode()
        action, payload = response[0], response[1:]

        if action == GAME_UPDATE:
            print(payload)

        elif action == INPUT_REQUIRED:
            payload, max_value = eval(payload)
            input_value = max_value + 1
            print(payload)

            while input_value > max_value:
                try:
                    input_value = int(input("Type in your choice\n>> "))
                except ValueError:
                    print("Non numeric value detected")
                    continue

            sock.sendall(str(input_value).encode())





if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: client.py <server-ip> <port>")
        sys.exit()

    player = PlayerClient()
    print(f"Connected to server on IP: {server_ip}, PORT: {server_port}")
    game = threading.Thread(target=game_thread)
    game.daemon = True
    game.start()

    while not GAME_OVER:
        time.sleep(1)




