#!/usr/bin/env python3
# Universidade Estadual de Feira de Santana
# Class: Advanced Distrybuted Systens
# Based on mcast.py File, available from:
#       http://svn.python.org/projects/python/branches/pep-0384/Demo/sockets/mcast.py
# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.

# Construa uma solucao para o multicast totalmente ordenado e confiavel em um
# sistema sincrono sendo base para solucao para o problema do consenso.

import time
import struct
import socket
import sys
import queue # Allow use all kind of Queue - It works only on python3
import threading # Allow use threads
#
# import queue
#
# q = queue.Queue()
#
# for i in range(5):
#     q.put(i)
#
# while not q.empty():
#     print(q.get(), end=' ')
# print()

class ProcessReceiver(threading.Thread):
    # Constructor
    def __init__(self, group, PORT):
        threading.Thread.__init__(self)
        self.logical_clock = 0
        # Group address
        self.group = group
        # Socket port
        self.PORT = PORT
        # Define if the thread is running
        self.running = True

    # Execute the thread
    def run(self):
        # Look up multicast group address in name server and find out IP version
        addrinfo = socket.getaddrinfo(self.group, None)[0]
        # Create a socket
        s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        # Allow multiple copies of this program on one machine
        # (not strictly needed)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind it to the port
        s.bind(('', self.PORT))
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
        # Join group
        if addrinfo[0] == socket.AF_INET: # IPv4
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            mreq = group_bin + struct.pack('@I', 0)
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

        while self.running:
            # print('* Waiting for messages: ')
            data, sender = s.recvfrom(1500)
            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            print ('\n\t\t === RECEIVED MESSAGE ===\n')
            print ('* From: ' + str(sender))
            print ('* Message: ' + repr(data)+"\n")

    # Destroy the thread
    def kill(self):
        self.running = False

def main():
    if( ("-h" or "--help" or "-H") in sys.argv[1:] ):
        print("\n\t\t=== SYSTEM HELP MENU ===")
        print("* Basic usage: ")
        print("** SimpleMulticast -h -H --help: Show Help Menu\n")
        # print("** SimpleMulticast -s -S --sender: Enable sender mode\n")
        print("** SimpleMulticast -6 --ipv6: Enable IPV6 mode\n")
        # print("** Otherwise: SET IPV4 and Receiver mode\n")
        print("** Otherwise: SET IPV4\n")
    else:
        if ( ("--ipv6" or "-6") in sys.argv[1:] ):
            print("\n\n")
            GROUP_IPV6 = input ('Insert Group address using ipv6 (default == "ff15:7079:7468:6f6e:6465:6d6f:6d63:6173)": ')
            if(GROUP_IPV6 == ""):
                GROUP_IPV6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
            group = GROUP_IPV6
        else:
            GROUP_IPV6 = input ('Insert Group address using ipv4 (default == "225.0.0.250"): ')
            if(GROUP_IPV6 == ""):
                GROUP_IPV4 = '225.0.0.250'
            group = GROUP_IPV4

        PORT = input ('Insert port value (default == 8123): ')
        if(PORT == ""):
            PORT = 8123

        TTL = input ('Insert the Time to Live value (default == 1): ')
        if(TTL == ""):
            TTL = 1 # Increase to reach other networks
        TTL = int(TTL)

        # start the receiver thread
        receiver = ProcessReceiver(group=group, PORT=PORT)
        receiver.start()
        # receiver.join()
        menu = -1
        while (menu < 2):
            print("\n\n\t\t === MULTICAST CHAT - MAIN MENU ===\n")
            print("[ 1 ] New event ")
            print("[ 2 ] Send a message to the Group ")
            print("[ 3 ] Sair ")
            menu = int(input("Choosen Menu: "))
            if(menu == 1):
                print("\n\t\t === NEW EVENT GENERATED ===")
                print("* Logical Clock Before: ", receiver.logical_clock)
                receiver.logical_clock += 1
                print("* Current Logical Clock: ", receiver.logical_clock)
            elif (menu == 2):
                # Send a message for multicast group
                sender(group, PORT, TTL)
            else:
                receiver.stop()
                sys.exit()
                break

def sender(group, PORT, TTL):
    addrinfo = socket.getaddrinfo(group, None)[0]

    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', TTL)
    if addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    print('\n\n=== CHAT VIA MULTICAST (SENDER) ===')
    print("* Tip: Send messages only for registered IPs addresses (on multicast group)\n")
    #while True:
        # data = repr(time.time()).encode('utf-8') + b'\0'
    data = input('Send a message to group: ').encode('utf-8')
    s.sendto(data, (addrinfo[4][0], PORT))
    time.sleep(1)

if __name__ == '__main__':
    main()
