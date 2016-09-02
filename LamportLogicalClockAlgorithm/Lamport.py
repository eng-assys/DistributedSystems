#!usr/bin/env python

'''
Atividade 02 - Implementar o algoritmo Relogio Logico de Lamport para tres processos comunicantes.
 Os processos podem se comunicar via UDP ou TCP.
'''
# Implementation of Lamport Logical Clock Algorithm
# Universidade Estadual de Feira de Santana
# Authors: Lucas Vinicius dos Santos Assis and Kelvin Ludwing
# Based on code available on: http://code.activestate.com/recipes/578591-primitive-peer-to-peer-chat/
import socket
import threading
import select
import time
import sys

class Process():
    """docstring for Process"""
    def __init__(self, port):
        self.server = ProcessServer(port=port)

    def send_message(self):
        self.server.logical_clock += 1
        message = "Generic message"
        print('\n\t === Sending Message ===')
        host = input("Insert the host to send message (Default == 127.0.0.1): ")
        port = input("Insert the port to send message (Default == 9005): ")
        message_input = input("Enter a custom message if you want: ")
        
        if(host == ''):
            host = '127.0.0.1'
        
        if(port == ''):
            port = '9005'
        
        if(not message_input == ''):
            message = message_input
        message += ('-' + str(self.server.logical_clock))

        print("\nMessage sent: '"+message.split('-')[0])
        print("Local logical clock: "+message.split('-')[1])
        print("To the address: ",host, ":", port)

        client = ProcessClient()

        client.connect_to(host=host, port=port)
        client.send_message(message)
        client.close()


# The class Client operates as a Thread to send messages from other peers in its
# Server sockets
class ProcessClient():
    # Constructor
    def __init__(self):
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def connect_to(self, host=None, port=None):
        if(host==None):
            host = '127.0.0.1'
        
        if(port==None):
            port = '9005'

        self.client_socket.connect((host, int(port)))

    def send_message(self, message):
        self.client_socket.send( message.encode() )
    def close(self):
        self.client_socket.close()

# The class Server operates as a Thread to receive messages from other peers
# in its Client sockets
class ProcessServer(threading.Thread):
    # Constructor
    def __init__(self, host=None, port=None):
        threading.Thread.__init__(self)
        self.logical_clock = 0
        self.running = True
        self.conn = None
        self.addr = None
        
        if(host==None):
            self.host = '127.0.0.1'
        else:
            self.host = host
        if(port==None):
            self.port = '9005'
        else:
            self.port = port

    # Execute the thread
    def run(self):
        HOST = self.host
        PORT = int(self.port)
        # It Defines socket like TCP and IPV4
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Associate socket server to an anddress and port
        server_socket.bind((HOST,PORT))
        # Server Will always listen
        server_socket.listen(1)
        # Select loop for listen
        while self.running:
            # Server waits a connection
            self.conn, self.addr = server_socket.accept()
            print("\n ---> Received connection from: ", self.addr)
            # This function receive data from connection
            received_data = self.conn.recv(1024).decode()
            received_data = str(received_data)
            if not received_data:
                break
            print('\n\t === Received Message ===')
            print("Complete received message: ", received_data)
            received_data = received_data.split('-')
            print ("Received Message Content: ", str(received_data[0]))
            print ("Received Logical Clock value: ", received_data[1])

            if(int(received_data[1]) > self.logical_clock):
                print("\nInner Logical clock, before: ", self.logical_clock)
                self.logical_clock = int(received_data[1])
            elif(int(received_data[1]) == self.logical_clock):
                print("\nLogical clock from message is equal to local logical clock, no changes to do")
            elif(int(received_data[1]) < self.logical_clock):
                print("\nLogical clock from message is lower than local logical clock, no changes to do")

            self.logical_clock += 1
            print("\nInner Logical clock, current: ", self.logical_clock)
            
            time.sleep(1)
    # Destroy the thread
    def kill(self):
        self.running = False

def main():    
    server_port = input("Insert the port to receive data (Default: 9005): ")
    if(server_port==''):
        server_port = '9005'

    process = Process(port=server_port)
    process.server.start()
    while True:
        print("\n\t\t === Running Process, Lamport Algorithm === ")
        print("* Possible actions: \n 'message_to' -> Send message to another process \n 'event' -> Create a new event  \n 'value' -> Logical Clock Value \n 'exit' -> Self explained")
        action = input("\nInsira uma ação desejada: ")
        if(action == "message_to"):
            process.send_message()
            time.sleep(0.5)
        elif(action == "event"):
            process.server.logical_clock += 1
            log_clock = process.server.logical_clock
            print("\n\t === New event created ===")
            print("* New logical clock: ", log_clock)
        elif(action == "value"):
            print("\n === Local Logical clock ===")
            print("Value", process.server.logical_clock)

        elif(action == "exit"):
            print("\nProcess Killed")
            
            process.server.stop()
            sys.exit()
            break
    #process.kill_server()

if __name__ == "__main__":
    main()