# !/usr/bin/python
# -- coding: utf-8 --

import random
import time
import socket
import sys
from constants import *
baraja1 = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
baraja2 = ["♣", "♥", "♠", "♦"]
baraja3 = []
jugadores = []
connected_players = []

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


    def get_player_info(self):
        return self.nick, self.mano, self.sets


def send_update_to_all_users(message):
    for connection in connections:
        print("SENDING STATUS", connection)
        connection.send(f"{GAME_UPDATE}{message}".encode())


def preguntar(jugador1, jugador2):
    poseidas = []
    cont = 1
    #choose = random.randint(0,len(jugador1.mano)-1)
    #value = jugador1.mano[choose][0] #carta a preguntar
    print("carta a preguntar: ")
    card_payload = "Card to ask for:"

    for x in jugador1.mano:
        print(cont,") "+str(x[0]+" "+x[1]))
        card_payload += f"\n{cont}) {x[0]} {x[1]}"
        cont +=1

    jugador1.socket.send(f"{INPUT_REQUIRED}{[card_payload, len(jugador1.mano)]}".encode())

    it = int(jugador1.socket.recv(BUFF_SIZE).decode())

    value = jugador1.mano[it-1][0]
    for carta in jugador2.mano:
        if carta[0] == value:
            poseidas.append(carta)
    for carta in poseidas:
        jugador2.mano.remove(carta)
    for carta in poseidas:
        jugador1.mano.append(carta)
    status = jugador1.nick+" le ha preguntado a  "+jugador2.nick+" si tiene la carta "+value+"s. "
    send_update_to_all_users(status)

    print()
    status = jugador2.nick+" tenia "+str(len(poseidas))+" cartas de "+value
    send_update_to_all_users(status)

    print(status)
    if len(poseidas) == 0:
        pescar(jugador1)
        status = "al jugador: "+jugador1.nick+" le toca pescar "
        send_update_to_all_users(status)
    else:
        checkeoDeSet(jugador1)
        jugador1.socket.send(f"{GAME_UPDATE}Your new deck is: {jugador1.mano}\nAnd your sets are: {jugador1.sets}".encode())
    print(status)

def pescar(jugador):
    print(baraja3)
    carta = baraja3.pop()
    jugador.mano.append(carta)
    jugador.socket.send(f"{GAME_UPDATE}Your new deck is: {jugador.mano}\nAnd your sets are: {jugador.sets}".encode())


def checkeoDeSet(jugador):
    cantidad = {}
    for carta in jugador.mano:
        if carta[0] not in cantidad.keys():
            cantidad[carta[0]] = 1
        elif carta[0] in cantidad.keys():
            cantidad[carta[0]] += 1
    for count in cantidad.keys():
        if cantidad[count] == 4:
            print("el jugador: "+jugador.nick+" tiene un set de "+count+"s.")
            send_update_to_all_users(f"{jugador.nick} has a set of {count}s!")
            jugador.sets.append(count)
            jugador.mano[:] = [carta for carta in jugador.mano if carta[0] != count]

def inicio():
    cant = 0
    err =0
    while(cant>5 or cant<1):
        cant =int(input("ingrese numero de jugadores (1-5): "))
        if(cant>5 or cant<1):
            err +=1
        if (err>0):
            print("input no valido")
        err = 0
    
def play(jugadores, deck):
    turn = 0
    size = 7 # cnaitdad de cartas por jugador
    dealt = 0
    order = jugadores
    for i in order:
        while dealt < size:
            pescar(i)
            #pescar(order[0])
            #pescar(order[1])
            #pescar(order[2])
            #pescar(order[3])
            dealt += 1
        dealt = 0

    while len(deck) != 0:
        for jugador in order:
            count = 0

            mano = "mano de "+jugador.nick+": "
            for carta in jugador.mano:
                if count < len(jugador.mano)-1:
                    mano += carta[0]+carta[1]+", "
                    count += 1
                elif count == len(jugador.mano)-1:
                    mano += carta[0]+carta[1]+"."
            print(mano)
            count = 0
            sets = "sets de "+jugador.nick
            for set in jugador.sets:
                if count < len(jugador.sets)-1:
                    sets += set+"s, "
                elif count == len(jugador.sets)-1:
                    sets += set+"s."
            print(sets)
        other_player = turn
        """ 
        while other_player == turn:
            other_player = random.randint(0,3) 
        """ #decidir a quien se le pregunta

        print("turno de :", order[turn].nick)
        connections[turn].send(f"{GAME_UPDATE}It's your turn, {order[turn].nick}".encode())
        print(" ---------------------------  ")
        print("a quien deseas preguntar?")
        cont = 0
        ask_payload = "Who do you want to ask for a card?"
        while other_player == turn:
            for j in order:
                if(cont != turn):
                    print(cont,") "+j.nick)
                    ask_payload += f"\n{cont}) {j.nick}"
                cont +=1
            cont = 1
            print("Sending payload", ask_payload)

            connections[turn].send((INPUT_REQUIRED + str([ask_payload, len(order) - 1])).encode())

            other_player = int(connections[turn].recv(BUFF_SIZE).decode())

        preguntar(order[turn], order[other_player])
        checkeoDeSet(order[turn])

        if turn >= len(order) - 1:
            turn = 0
        else:
            turn += 1
        time.sleep(3)
        print("=========================================")


    return True



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

        while len(connected_players) < len(jugadores):
            print("Waiting for players... ")
            conn, addr = sock.accept()
            print(f"One player entered!")
            connected_players.append(addr)
            connections.append(conn)
            print(connections[-1])
            nickname = connections[-1].recv(BUFF_SIZE).decode()
            print(f"Your nickname is now {nickname}")
            jugadores[len(connections) - 1].nick = nickname
            jugadores[len(connections) - 1].socket = conn

            player = jugadores[len(connections) - 1]

            connections[-1].send(str([player.mano, player.sets]).encode())
            print(f"Sent username & deck to player {len(connections)} ({nickname})")

        print("Game ready!")
    play(jugadores, baraja3)




