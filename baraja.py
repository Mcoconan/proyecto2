# !/usr/bin/python
# -- coding: utf-8 --
"""
    baraja.py
    Authors: Mario Sarmientos, Randy Venegas, Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated September 23, 2021
    Server side of Go Fish game using TCP encrypted sockets.
"""

import random
import time
import socket
import sys
import threading
from cryptography.fernet import Fernet
from constants import *


f = Fernet(b'QKJckJwoLx8kT10gslNc4_IEE4fNYZyluOaK2m5fwmE=')


def encrypt(message):
    return f.encrypt(message)


def decrypt(message):
    return f.decrypt(message)


baraja1 = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
baraja2 = ["♣", "♥", "♠", "♦"]
baraja3 = []
jugadores = []
connected_players = []
game_over = [False]
"""
creación del mazo de juego
"""
for i in baraja2:
    for j in baraja1: 
        baraja3.append([j,i])
random.shuffle(baraja3)




"""
funcion con la cual se pregunta si posee x carta
"""


class jugador(): 
    def __init__(self):
        self.nick = ""      # nick del jugador
        self.mano = []      # cartas que poseee en su mano
        self.sets = []      # sets completados
        self.socket = None  # socket

    def get_deck_string(self):
        deck = ""
        for card in self.mano:
            deck += f"{card[0]}{card[1]}\n"

        return deck


    def get_player_info(self):
        return self.nick, self.mano, self.sets


def send_update_to_all_users(message, exclude=None):
    for connection in connections:
        if connection != exclude:
            time.sleep(0.5)
            connection.sendall(encrypt(f"{GAME_UPDATE}{message}".encode()))


def preguntar(jugador1, jugador2):
    poseidas = []
    cont = 1
    #choose = random.randint(0,len(jugador1.mano)-1)
    #value = jugador1.mano[choose][0] #carta a preguntar
    print("card to ask for: ")
    card_payload = "Card to ask for:"

    for x in jugador1.mano:
        print(cont,") "+str(x[0]+" "+x[1]))
        card_payload += f"\n{cont}) {x[0]} {x[1]}"
        cont +=1
    time.sleep(0.5)
    jugador1.socket.sendall(encrypt(f"{INPUT_REQUIRED}{[card_payload, len(jugador1.mano)]}".encode()))

    it = int(decrypt(jugador1.socket.recv(BUFF_SIZE)).decode())

    value = jugador1.mano[it-1][0]
    for carta in jugador2.mano:
        if carta[0] == value:
            poseidas.append(carta)
    for carta in poseidas:
        jugador2.mano.remove(carta)
    for carta in poseidas:
        jugador1.mano.append(carta)
    status = jugador1.nick+" has asked  "+jugador2.nick+" for "+value+"s. "
    send_update_to_all_users(status)

    print()
    status = jugador2.nick+" had "+str(len(poseidas))+" cards of value "+value
    send_update_to_all_users(status)

    print(status)
    if len(poseidas) == 0:
        pescar(jugador1)
        status = "Go fish, "+jugador1.nick+"!"
        print(status)
        send_update_to_all_users(status)
        return False
    else:
        checkeoDeSet(jugador1)
        time.sleep(0.5)
        jugador1.socket.sendall(encrypt(f"{GAME_UPDATE}Your new deck is:\n{jugador1.get_deck_string()}\nAnd your sets are: {jugador1.sets}".encode()))
        return True


def pescar(jugador, logging=True):
    print(baraja3)
    carta = baraja3.pop()
    jugador.mano.append(carta)
    if logging:
        time.sleep(0.5)
        jugador.socket.sendall(encrypt(f"{GAME_UPDATE}Your new deck is: {jugador.get_deck_string()}\nAnd your sets are: {jugador.sets}".encode()))


def checkeoDeSet(jugador):
    cantidad = {}
    for carta in jugador.mano:
        if carta[0] not in cantidad.keys():
            cantidad[carta[0]] = 1
        elif carta[0] in cantidad.keys():
            cantidad[carta[0]] += 1
    for count in cantidad.keys():
        if cantidad[count] == 4:
            print("Player: "+jugador.nick+" has a set of "+count+"s.")
            send_update_to_all_users(f"{jugador.nick} has a set of {count}s!")
            jugador.sets.append(count)
            jugador.mano[:] = [carta for carta in jugador.mano if carta[0] != count]

def inicio():
    cant = 0
    err =0
    while(cant>5 or cant<1):
        cant =int(input("Type in the number of players (2-5): "))
        if(cant>5 or cant<1):
            err +=1
        if (err>0):
            print("Invalid input")
        err = 0
    for i in range(cant):
        jugadores.append(jugador())
    
def play(jugadores, deck):
    turn = 0
    size = 7 # cnaitdad de cartas por jugador
    dealt = 0
    order = jugadores
    for i in order:
        while dealt < size:
            pescar(i, logging=False)
            dealt += 1
        dealt = 0
        time.sleep(0.5)
        i.socket.sendall(encrypt(f"{GAME_UPDATE}Your deck is:\n{i.get_deck_string()}".encode()))



    while len(deck) != 0:
        for jugador in order:
            count = 0

            mano = "deck of player: "+jugador.nick+": "
            for carta in jugador.mano:
                if count < len(jugador.mano)-1:
                    mano += carta[0]+carta[1]+", "
                    count += 1
                elif count == len(jugador.mano)-1:
                    mano += carta[0]+carta[1]+"."
            print(mano)
            count = 0
            sets = "sets of player: "+jugador.nick
            for set in jugador.sets:
                if count < len(jugador.sets)-1:
                    sets += set+"s, "
                elif count == len(jugador.sets)-1:
                    sets += set+"s."
            print(sets)
        other_player = turn

        print(f"{order[turn].nick}'s turn!")
        time.sleep(0.5)
        connections[turn].sendall(encrypt(f"{GAME_UPDATE}It's your turn, {order[turn].nick}".encode()))

        keep_asking = True
        checkeoDeSet(order[turn])
        if len(order[turn].mano) == 0:
            pescar(order[turn], logging=True)
            keep_asking = False
        while keep_asking:
            cont = 0
            ask_payload = "Who do you want to ask for a card?"
            for j in order:
                if(cont != turn):
                    print(cont,") "+j.nick)
                    ask_payload += f"\n{cont}) {j.nick}"
                cont +=1
            cont = 1

            time.sleep(0.5)
            connections[turn].sendall(encrypt((INPUT_REQUIRED + str([ask_payload, len(order) - 1])).encode()))

            other_player = int(decrypt(connections[turn].recv(BUFF_SIZE)).decode())

            keep_asking = preguntar(order[turn], order[other_player])

        time.sleep(0.5)
        connections[turn].sendall(encrypt(f"{CHAT}Placeholder chat".encode()))
        message = decrypt(connections[turn].recv(BUFF_SIZE)).decode()
        if message != "#%EmptyMessage#%":
            send_update_to_all_users(f"{jugadores[turn].nick}: {message}", exclude=connections[turn])
        print("Finished the update")

        if turn >= len(order) - 1:
            turn = 0
        else:
            turn += 1
        time.sleep(3)
        print("=========================================")

    game_over[0] = True

    leaderboard = {}
    for player in jugadores:
        if len(player.sets) not in leaderboard.keys():
            leaderboard[len(player.sets)] = [player.nick]
        else:
            leaderboard[len(player.sets)].append(player.nick)

    leaderboard_keys = sorted(list(leaderboard.keys()))
    counter = 1
    leaderboard_payload = "GAME OVER!\nLEADERBOARD:"
    while len(leaderboard_keys) > 0:
        f"\n{counter}: {leaderboard[leaderboard_keys.pop()]}"
        counter += 1

    send_update_to_all_users(leaderboard_payload)
    return game_over


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: baraja.py <port>")
        sys.exit()

    inicio()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with sock as sock:
        server_port = int(sys.argv[1])
        server_address = (HOST, server_port)

        sock.bind(server_address)
        sock.listen(5)

        connections = []
        print(len(connected_players), len(jugadores))
        while len(connected_players) < len(jugadores):
            print("Waiting for players... ")
            conn, addr = sock.accept()
            print(f"One player entered!")

            connected_players.append(addr)
            connections.append(conn)

            nickname = decrypt(connections[-1].recv(BUFF_SIZE)).decode()
            jugadores[len(connections) - 1].nick = nickname
            jugadores[len(connections) - 1].socket = conn

            player = jugadores[len(connections) - 1]

            connections[-1].sendall(encrypt(f"{GAME_UPDATE}Your deck is: {[player.mano, player.sets]}".encode()))
            print(f"Sent username & deck to player {len(connections)} ({nickname})")

        print("Game ready!")
    game = threading.Thread(target=play, args=(jugadores, baraja3))
    game.start()





