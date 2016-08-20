# Implementation of Christian Algorithm's Client with real local clock adjustment
# Universidade Estadual de Feira de Santana
# Distributed System Class
# Authors: Lucas Vinícius dos Santos Assis and Kelvin Ludwing
# Based on Client code available from:  https://shakeelosmani.wordpress.com/2015/04/13/python-3-socket-programming-example/

'''
    Atividade 01 - Fazer um cliente e um servidor que implementem o algoritmo de Christian.
    * O cliente deverá ser configurável para fazer n pedidos ao servidor antes de escolher o 
        menor RTT para setar seu clock. 
    * O servidor NÃO SERÁ SINCRONIZADO com uma fonte externa. 
    * Cliente e servidor devem se comunicar por UDP.
'''
import socket
from datetime import datetime
 
def main():
    # When the client sends the request to Server
    time_1 = []
    # When the server receives the request from Client
    time_2 = []
    # When the Server sends the response from Server
    time_3 = []
    # When the client receives the response from Server
    time_4 = []

    print('\n\t\t=== CLIENT === ')
    print('* Current Date and time: ', datetime.now())

    # Define Host address
    host = input("Insert 'HOST' address (Default == localhost): ")
    if(host == ''):
        host = "127.0.0.1"

    # Define the port value
    port = input("Insert 'PORT' number (Default == 5999): ")
    if (port == ''):
        port = 5999    
    elif( port.isdigit() ):
        port = int (port)
    else:
        print ("Invalid Port value inserted")
        return
         
    # Define number of requests
    request_number = input("Insert the number of requests to the server (Default == 5): ")
    if (request_number == ''):
        request_number = 5
    elif( request_number.isdigit() ):
        request_number = int (request_number)
    else:
        print ("Invalid number od requests inserted")
        return

    # Protocol message
    request_type = "time_adjustment"

    client_socket = socket.socket()
    client_socket.connect((host,port))

    for i in range(0, request_number):
        print('\t === Request', i, '===')
        # The request message is composed by type of request and current date and time of client
        # Get the current clock when it sends request to server
        time_1.append( str(datetime.now()) )
        print('T1: ', time_1[-1])
        request_message = request_type +'@'+ time_1[-1]

        # Send the message to server
        client_socket.send( request_message.encode() )
        # Received response from server - Buffer size is 1024
        received_data = client_socket.recv(1024).decode()
        # Get the current clock when it receives the response  from server
        time_4.append( str(datetime.now()) )

        received_data = str(received_data).split('@')

        time_2.append(received_data[0])
        time_3.append(received_data[1])

        print('T2: ', time_2[-1])
        print('T3: ', time_3[-1])
        print('T4: ', time_4[-1])

    client_socket.close()

    smaller_delay = get_delay(time_1[0], time_2[0], time_3[0], time_4[0])
    delay_id = 0
    print('\n\nInitial Smaller delay: ', smaller_delay)
    print('Delay ID: ', delay_id)

    for i in range(1, request_number):
        analised_delay = get_delay(time_1[i], time_2[i], time_3[i], time_4[i])

        print('\nCurrent analised delay: ', analised_delay)
        print('Delay ID: ', i)
        if(analised_delay < smaller_delay):
            smaller_delay = analised_delay
            delay_id = i

    print('\nFinal Smaller delay: ', smaller_delay)
    print('Delay ID: ', delay_id)

    print('\t=== Clock Adjustment ===')
    t1 = str_to_time(time_1[delay_id])
    t2 = str_to_time(time_2[delay_id])
    clock_adjustment = t2 - (t1 + smaller_delay/2)
    print('Value', clock_adjustment)

    # After receive the Clock information is necessary adjust
    # the client's clock according one of the follow situations
    # Late client
    # Early customer
    # Timely customer - No change

def get_delay(t1, t2, t3, t4):
    t1 = str_to_time(t1)
    t2 = str_to_time(t2)
    t3 = str_to_time(t3)
    t4 = str_to_time(t4)
    return (t4 - t1) - (t3 - t2)

def str_to_time(t):
    return datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')

if __name__ == '__main__':
    main()
