import random 
import time
import socket
import sys
from constants import *
baraja1 = ["A","2","3","4","5","6","7","8","9","10","J","D","R"]
baraja2 = [" de Treboles"," de corazones"," de picas"," de diamantes"]
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

def preguntar(jugador1,jugador2):
    print("preguntar")


class jugador(): 
    def __init__(self):
        self.nick = "" #nick del jugador
        self.mano = [] #cartas que poseee en su mano
        self.sets = [] #sets completados

    def get_player_info(self):
        return self.nick, self.mano, self.sets


def preguntar(jugador1, jugador2):
    poseidas = []
    cont = 1
    #choose = random.randint(0,len(jugador1.mano)-1)
    #value = jugador1.mano[choose][0] #carta a preguntar
    print("carta a preguntar: ")
    for x in jugador1.mano:
        print(cont,") "+str(x[0]+" "+x[1]))
        cont +=1
    it = int(input("escoge una carta: "))
    value = jugador1.mano[it-1][0]
    for carta in jugador2.mano:
        if carta[0] == value:
            poseidas.append(carta)
    for carta in poseidas:
        jugador2.mano.remove(carta)
    for carta in poseidas:
        jugador1.mano.append(carta)
    status = jugador1.nick+" le ha preguntado a  "+jugador2.nick+" si tiene la carta "+value+"s. "
    print()
    status = jugador2.nick+" tenia "+str(len(poseidas))+" cartas de "+value
    print(status)
    if len(poseidas) == 0:
        pescar(jugador1)
        status = "al jugador: "+jugador1.nick+" le toca pescar "
    print(status)

def pescar(jugador):
    print(baraja3)
    carta = baraja3.pop()
    jugador.mano.append(carta)

def checkeoDeSet(jugador):
    cantidad = {}
    for carta in jugador.mano:
        if carta[0] not in cantidad.keys():
            cantidad[carta[0]] = 1
        if carta[0] in cantidad.keys():
            cantidad[carta[0]] += 1
    for count in cantidad.keys():
        if cantidad[count] == 4:
            print("el jugador: "+jugador.nick+" tiene un set de "+count+"s.")
            jugador.sets.append(count)
            jugador.mano[:] = [carta for carta in jugador.mano if carta[0] == count]

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
    for i in range(0,int(cant)):
        jugadores.append(jugador())
        nombre = input("ingrese nombre del jugador "+str(i+1)+": ")
        jugadores[i].nick = nombre 
    
def play(jugadores, deck):
    turn = 0
    size = 7 # cnaitdad de cartas por jugador
    dealt = 0 
    random.shuffle(jugadores) #orden de los jugadores
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
            other_player = random.randint(0,3) """ #decidir a quien se le pregunta
        print("turno de :",order[turn].nick)
        print(" ---------------------------  ")
        print("a quien deseas preguntar?")
        cont = 0
        while other_player == turn:
            for j in order:
                if(cont != turn):
                    print(cont,") "+j.nick)
                cont +=1
            cont = 1
            other_player= int(input("tu eleccion: "))        
        preguntar(order[turn], order[other_player])
        checkeoDeSet(order[turn])
        if turn >= len(order):
            turn = 0
        else:
            turn += 1
        time.sleep(3)
        print("=========================================")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: baraja.py <port>")
        sys.exit()

    inicio()
    play(jugadores, baraja3)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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

        print("Game ready!")



