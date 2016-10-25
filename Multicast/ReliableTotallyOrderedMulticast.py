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
import random
import struct
import socket # Allow use udp and tcp sockets
import sys
import Queue # Allow use all kind of Queue - It works only on python2
import threading # Allow use threads
# Allow use grafic interface
from Tkinter import *
import ttk #  separator

def main():
    # DEFINING INITIAL INFORMATION
    # ==========================================================================
    if( ("-h" or "--help" or "-H") in sys.argv[1:] ):
        print("\n\t\t\t=== SYSTEM HELP MENU ===\n")
        print("* Basic usage: ")
        print("** ReliableTottallyOrderedMulticast -h -H --help: Show Help Menu\n")
        # print("** SimpleMulticast -s -S --sender: Enable sender mode\n")
        print("** ReliableTottallyOrderedMulticast -6 --ipv6: Enable IPV6 mode\n")
        # print("** Otherwise: SET IPV4 and Receiver mode\n")
        print("** Otherwise: Set IPV4\n")
    else:
        if ( ("--ipv6" or "-6") in sys.argv[1:] ):
            print("\n\n")
            GROUP_IPV6 = raw_input ('Insert Group address using ipv6 (default == "ff15:7079:7468:6f6e:6465:6d6f:6d63:6173)": ')
            if(GROUP_IPV6 == ""):
                GROUP_IPV6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
            group = GROUP_IPV6
        else:
            GROUP_IPV6 = raw_input ('Insert Group address using ipv4 (default == "225.0.0.250"): ')
            if(GROUP_IPV6 == ""):
                GROUP_IPV4 = '225.0.0.250'
            group = GROUP_IPV4

        PORT = raw_input ('Insert port value (default == 8123): ')
        if(PORT == ""):
            PORT = 8123
        else:
            PORT = int(PORT)

        TTL = raw_input ('Insert the Time to Live value (default == 1): ')
        if(TTL == ""):
            TTL = 1 # Increase to reach other networks
        else:
            TTL = int(TTL)

        PROCESS_ID = raw_input ('Insert the PROCESS ID (DEFAULT = RANDOM(1-30000)): ')
        if(PROCESS_ID == ""):
            PROCESS_ID = str(random.randint(1, 30000))

        # DICTIONARY WITH ALL SENT MESSAGES
        sent_messages = {}

        # ==========================================================================
        # BUILDING THE GRAFIC USER INTERFACE
        # ---------------------------------- RECEIVED MESSAGE WINDOW
        multicast = Tk() # Window to show received information
        multicast.wm_title("MULTICAST APPLICATION (ID: "+PROCESS_ID+")")
        multicast.resizable(0,0)

        scrollbar = Scrollbar(multicast)
        scrollbar.pack(side=RIGHT, fill=Y)

        multicast.grid_columnconfigure(0, weight=1)
        text_receiver = Text(multicast)

        text_receiver.pack()

        # attach Text area to scrollbar
        text_receiver.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_receiver.yview)

        # ==========================================================================
        label_clock = Label(multicast, font = "Verdana 12 bold", text='Clock: ')
        # START THE RECEIVER THREAD - LISTENING TO THE OTHERS COMPONENTS
        receiver = MulticastReceiver(group=group,
                                        PORT=PORT,
                                        text_receiver=text_receiver,
                                        label_clock=label_clock)
        receiver.start()
        label_clock['text'] = 'Clock: '+str(receiver.logical_clock)
        label_clock.pack(side=TOP)
        # FUNCTION OF ACTIONS TO THE MENU BUTTONS
        # -----------------------------------
        def sendMessage():
            message = message_entry.get()
            if(message == ""):
                message = "empty"
            text_receiver.insert(INSERT, "\n\n\n\n")
            sent_messages[receiver.logical_clock + 1] = message
            sender(group=group,
                    PORT=PORT,
                    TTL=TTL,
                    logical_clock=receiver.logical_clock + 1,
                    message=message,
                    text_receiver=text_receiver,
                    label_clock=label_clock,
                    PROCESS_ID=PROCESS_ID,
                    attempt_number=2)
            receiver.logical_clock += 1

            print(sent_messages)

        def clearText():
            text_receiver.delete('1.0', END)
            text_receiver.insert(INSERT, "\t\t\t=== RELIABLE AND TOTALLY ORDERED MULTICAST ===\n")

        def exitProgram():
            multicast.destroy()
            receiver.exit()
            sys.exit()

        def showSentMSG():
            text_receiver.insert(INSERT, "\n\t\t\t=== SENT MESSAGES ===\n")
            for key, value in sent_messages.iteritems():
                text_receiver.insert(INSERT, '* Clock: '+str(key)+' -> Message: '+str(value)+"\n")
            print(sent_messages)

        def showRCVMSG():
            text_receiver.insert(INSERT, "\n\t\t\t=== RECEIVED MESSAGES ===\n")
            for key, value in receiver.received_messages.iteritems():
                print("PROCESS ID: ", key, "Value: ", value.queue)
                text_receiver.insert(INSERT, "PROCESS ID OF SENDER: "+str(key)+" - (Clock, message): "+str(value.queue)+"\n")

        label_message = Label(multicast, text='MSG to Group: ')
        label_message.pack(side=LEFT)
        message_entry = Entry(multicast)
        message_entry.pack(side=LEFT)
        B_send = Button(multicast, text ="Send", command = sendMessage)
        B_send.pack(side=LEFT)
        B_clear = Button(multicast, text ="Clear", command = clearText)
        B_clear.pack(side=LEFT)

        B_sent_msg = Button(multicast, text ="Sent MSG", command = showSentMSG)
        B_sent_msg.pack(side=LEFT)

        B_rcv_msg = Button(multicast, text ="RCV MSG", command = showRCVMSG)
        B_rcv_msg.pack(side=LEFT)

        text_receiver.insert(INSERT, "\t\t\t=== RELIABLE AND TOTALLY ORDERED MULTICAST ===\n")

        # START THE WINDOW EXECUTION
        multicast.mainloop()

def sender(group, PORT, TTL, logical_clock, message, text_receiver, label_clock, PROCESS_ID, attempt_number):
    # How many mebers there are in multicast group
    group_view = 0
    # How many mebers sent ack messages after delivering
    group_ack = 0
    original_message = message
    addrinfo = socket.getaddrinfo(group, None)[0]

    sender_socket = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    sender_socket.settimeout(2)
    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', TTL)
    if addrinfo[0] == socket.AF_INET: # IPv4
        sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        sender_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    # GET the Group view
    sender_socket.sendto( ("@@GROUPVIEW@@").encode('utf-8') , (addrinfo[4][0], PORT))
    while True:
        try:
            data, server = sender_socket.recvfrom(16)
            if ( "@@ACKGROUPVIEW@@" in data ):
                group_view += 1
                text_receiver.insert(INSERT, "* Ack #"+str(group_view)+" of group view on address: "+str(server)+"\n")
        except socket.timeout:
            text_receiver.insert(INSERT, '* Total number of group members: '+str(group_view)+'\n')
            break

    text_receiver.insert(INSERT, "\n\t\t\t=== SENDING MESSAGE ===\n")
    text_receiver.insert(INSERT, "* Message: "+message+"\n")
    # Insert logical clock in the message
    message = str(logical_clock) + "@#@" + message + "@#@" + PROCESS_ID
    data = ( message ).encode('utf-8')
    sender_socket.sendto(data, (addrinfo[4][0], PORT))
    label_clock['text'] = 'Clock: '+str(logical_clock)
    while True:
        try:
            data, server = sender_socket.recvfrom(16)
            if( "@@ACKMESSAGE@@" in data ):
                group_ack += 1
                text_receiver.insert(INSERT, "\nACK received from #"+str(group_ack)+" on address: "+str(server)+"\n")
        except socket.timeout:
            text_receiver.insert(INSERT, '* Timed out - ack receivement\n')
            break
    sender_socket.close()
    if (group_ack == group_view):
        text_receiver.insert(INSERT, "\n* Totally Reliable Delivery guaranteed\n")
    else:
        text_receiver.insert(INSERT, "\n* Totally Reliable Delivery not guaranteed, resending message\n")
        if (attempt_number == 0):
            text_receiver.insert(INSERT, "\n* Last attempt\n")
            return
        else:
            # Trying resend the message to the group
            sender(group=group,
                    PORT=PORT,
                    TTL=TTL,
                    logical_clock=logical_clock,
                    message=original_message,
                    text_receiver=text_receiver,
                    label_clock=label_clock,
                    PROCESS_ID=PROCESS_ID,
                    attempt_number=attempt_number - 1)

class MulticastReceiver(threading.Thread):
    # Constructor
    def __init__(self, group, PORT, text_receiver, label_clock):
        threading.Thread.__init__(self)
        # Lamport Logical clock value
        self.logical_clock = 0
        # Group address
        self.group = group
        # Socket port
        self.PORT = PORT
        # Used to print received info to the grafic interface
        self.text_receiver = text_receiver
        self.label_clock = label_clock
        # Define if the thread is running
        self.running = True
        self.received_messages = {}

    # Execute the thread
    def run(self):

        # Look up multicast group address in name server and find out IP version
        addrinfo = socket.getaddrinfo(self.group, None)[0]
        # Create a socket
        sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        # Allow multiple copies of this program on one machine
        # (not strictly needed)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind it to the port
        sock.bind(('', self.PORT))
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
        # Join group
        if addrinfo[0] == socket.AF_INET: # IPv4
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            mreq = group_bin + struct.pack('@I', 0)
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

        while self.running:
            # print('* Waiting for messages: ')
            data, sender = sock.recvfrom(1500)

            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            message = repr(data)
            print(message)
            ack = ""
            # To counting purpose
            if ( "@@GROUPVIEW@@" in message ):
                ack = ('@@ACKGROUPVIEW@@').encode('utf-8')
            else:
                message = message.split("@#@")
                try:
                    print(self.received_messages[message[2]])
                except KeyError:
                    self.received_messages[message[2]] = Queue.PriorityQueue(maxsize=0)
                received_clock = int(message[0][1:])
                if(received_clock > self.logical_clock):
                    self.logical_clock = received_clock
                self.logical_clock += 1
                self.label_clock['text'] = 'Clock: '+str(self.logical_clock)

                self.received_messages[message[2]].put( (int(message[0][1:]), message[1]) )

                self.text_receiver.insert(INSERT, '\n\t\t\t === RECEIVED MESSAGE ===\n')
                self.text_receiver.insert(INSERT, '* From: ' + str(sender) + '\n')
                self.text_receiver.insert(INSERT, '* Message: ' + message[1] + '\n')

                self.text_receiver.insert(INSERT, '* Sending acknowledgement to: ' + str(sender) + '\n')
                ack = ('@@ACKMESSAGE@@').encode('utf-8')
            sock.sendto(ack, sender)

    def stop(self):
        self.running = False
    def close(self):
        self.running = False
    def exit(self):
        self.running = False

if __name__ == '__main__':
    main()
