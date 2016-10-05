# Projete e implemente um protocolo para multicast basico sobre multicast IP;
import socket
import struct
import sys


# multicast_group = '224.3.29.71'
# Define multicast group address
multicast_group = raw_input('Insert the multicast group address: ')
if (multicast_group == ""):
    multicast_group = '224.3.29.71'

server_address = ('', 10000)

# The first step to establishing a multicast receiver is to create the UDP socket.
# Create the socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
udp_sock.bind(server_address)
# After the regular socket is created and bound to a port, it can be added to the multicast group by using setsockopt() to change the IP_ADD_MEMBERSHIP option. The option value is the 8-byte packed representation of the multicast group address followed by the network interface on which the server should listen for the traffic, identified by its IP address. In this case, the receiver listens on all interfaces using INADDR_ANY.

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# The main loop for the receiver is just like the regular UDP echo server.

# Receive/respond loop
while True:
    print ("=== SIMPLE MULTICAST RECEIVER ===\n")
    print ('* Waiting to receive message')
    data, address = udp_sock.recvfrom(1024)
    # print ('=> Received some data from: %s\n' % address)
    print address
    print data
    # print ('* Size of data: %s bytes' % str(len(data)))

    print ('* Data: ', data, '\n')

    print ('* Sending acknowledgement to: ', address)>>sys.stderr,
    udp_sock.sendto('ack', address)
