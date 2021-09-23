"""
    player_client.py
    Authors: Mario Sarmientos, Randy Venegas, Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated September 23, 2021
    Client side of Go Fish game using TCP encrypted sockets.
"""

import socket
import sys
import threading
import time
from cryptography.fernet import Fernet
from constants import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
GAME_OVER = False


f = Fernet(b'QKJckJwoLx8kT10gslNc4_IEE4fNYZyluOaK2m5fwmE=')


def encrypt(message):
    return f.encrypt(message)


def decrypt(message):
    return f.decrypt(message)


class PlayerClient:
    def __init__(self):
        nickname = input("Please specify your nickname:\n>> ")
        sock.connect((server_ip, server_port))
        sock.sendall(encrypt(bytes(nickname, encoding='ascii')))
        data = decrypt(sock.recv(1024))
        self.nick = nickname
        self.deck, self.sets = ('Received', eval(repr(data)))


def game_thread():
    """
    This function handles messaging
    """
    while not GAME_OVER:
        response, _ = sock.recvfrom(BUFF_SIZE)
        response = decrypt(response).decode()
        action, payload = response[0], response[1:]
        print("ACTION RECEIVED", action)
        if action == GAME_UPDATE:
            print(f"\n{payload}")

        elif action == INPUT_REQUIRED:
            payload, max_value = eval(payload)
            input_value = max_value + 1
            print(f"\n{payload}")

            while input_value > max_value:
                try:
                    input_value = int(input("Type in your choice\n>> "))
                except ValueError:
                    print("Non numeric value detected")
                    continue

            sock.sendall(encrypt(str(input_value).encode()))

        elif action == CHAT:
            chat = input("Type a message to chat with the room (enter to skip & end your turn): \n>> ")
            if len(chat) > 0:
                sock.sendall(encrypt(chat.encode()))
            else:
                sock.sendall(encrypt("#%EmptyMessage#%".encode()))
            print("******************\nYour turn has finished\n******************")


def send_chat():
    message = input("Type in your message:\n>> ")
    sock.sendall(encrypt(message.encode()))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: client.py <server-ip> <port>")
        sys.exit()

    player = PlayerClient()
    print(f"Connected to server on IP: {server_ip}, PORT: {server_port}\n")
    game = threading.Thread(target=game_thread)
    game.daemon = True
    game.start()

    while not GAME_OVER:
        time.sleep(1)





