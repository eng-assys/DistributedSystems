# Implementation of Christian Algorithm's Server with real local clock adjustment
# Universidade Estadual de Feira de Santana
# Distributed System Class
# Authors: Lucas Vinícius dos Santos Assis and Kelvin Ludwing
# Based on Server code available from:  https://shakeelosmani.wordpress.com/2015/04/13/python-3-socket-programming-example/

'''
    Atividade 01 - Fazer um cliente e um servidor que implementem o algoritmo de Christian.
    * O cliente deverá ser configurável para fazer n pedidos ao servidor antes de escolher o 
        menor RTT para setar seu clock. 
    * O servidor NÃO SERÁ SINCRONIZADO com uma fonte externa. 
    * Cliente e servidor devem se comunicar por UDP.
'''

import socket
from datetime import datetime

def Main():

    print('\n\t\t=== SERVER === ')
    print( '* Current Date and time: ', datetime.now() )

    # Define Host address
    host = input("Insert 'HOST' address (Default - localhost): ")
    if(host == ''):
        host = "127.0.0.1"

    # Define the port value
    port = input("Insert 'PORT' number (Default - 5999): ")
    if (port == ''):
        port = 5999    
    elif( port.isdigit() ):
        port = int (port)
    else:
        print ("Invalid Port value inserted")
        return

    server_socket = socket.socket()
    server_socket.bind((host,port))
    server_socket.listen(1)
    
    print('Accepting connection from '+host+':'+str(port) )
    conn, addr = server_socket.accept()
    
    print ("Received connection from: " + str(addr))
    
    while True:
        # Buffer size is 1024
        received_data = conn.recv(1024).decode()
        time_2 = str(datetime.now())
        
        # If receive no data, finish the server
        if not received_data:
            break

        received_data = str(received_data).split('@')
        print ("Request type from connected  user: " + received_data[0])

        if(received_data[0] == "time_adjustment"):
            received_data = time_2 + '@' + str( datetime.now() )
        else:
            received_data = str(received_data).upper()

        print ("sending: " + received_data)
        conn.send(received_data.encode())
             
    conn.close()
     
if __name__ == '__main__':
    Main()
