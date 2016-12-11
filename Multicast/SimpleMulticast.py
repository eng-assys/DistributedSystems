#!/usr/bin/env python3
# Universidade Estadual de Feira de Santana
# Class: Advanced Distrybuted Systens
# Based on mcast.py File, available from:
#       http://svn.python.org/projects/python/branches/pep-0384/Demo/sockets/mcast.py
# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.

# Projete e implemente um protocolo para multicast basico sobre multicast IP;

import time
import struct
import socket
import sys

def main():
    if( ("-h" or "--help" or "-H") in sys.argv[1:] ):
        # Usage:
        #   mcast -s (sender, IPv4)
        #   mcast -s -6 (sender, IPv6)
        #   mcast    (receivers, IPv4)
        #   mcast  -6  (receivers, IPv6)
        print("\n\t\t=== SYSTEM HELP MENU ===")
        print("* Basic usage: ")
        print("** SimpleMulticast -h -H --help: Show Help Menu\n")
        print("** SimpleMulticast -s -S --sender: Enable sender mode\n")
        print("** SimpleMulticast -6 --ipv6: Enable IPV6 mode\n")
        print("** Otherwise: SET IPV4 and Receiver mode\n")
    else:
        if ( ("--ipv6" or "-6") in sys.argv[1:] ):
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

        if "-s" in sys.argv[1:] or "-S" in sys.argv[1:] or "--sender" in sys.argv[1:]:
            sender(group, PORT, TTL)
        else:
            receiver(group, PORT)

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
    while True:
        # data = repr(time.time()).encode('utf-8') + b'\0'
        data = input('Send a message to group: ').encode('utf-8')
        s.sendto(data, (addrinfo[4][0], PORT))
        time.sleep(1)

def receiver(group, PORT):
    print('\n\n=== CHAT VIA MULTICAST (RECEIVER) ===\n')
    # Look up multicast group address in name server and find out IP version
    addrinfo = socket.getaddrinfo(group, None)[0]

    # Create a socket
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    s.bind(('', PORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
    if addrinfo[0] == socket.AF_INET: # IPv4
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        mreq = group_bin + struct.pack('@I', 0)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    # Loop, printing any data we receive
    while True:
        print('* Waiting for messages: ')
        data, sender = s.recvfrom(1500)
        while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
        print('Message from: ' + str(sender) + ' data: ' + repr(data)+"\n")

if __name__ == '__main__':
    main()
