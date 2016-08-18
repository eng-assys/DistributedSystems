# Available from:  https://shakeelosmani.wordpress.com/2015/04/13/python-3-socket-programming-example/

# First we import the python socket library.
import socket
# Then we define a main function
def Main():
    # We define two variables, a host and a port, 
    # here the local machine is the host thus ip address of 127.0.0.1 

    host = "127.0.0.1"
    # I have chosen randomly port 5000 and it is advised to use anything above 1024
    # as upto 1024 core services use the ports
    port = 5000
    # Then we define a variable mySocket which is an instance of a Python socket
    mySocket = socket.socket()
    # In server it is important to bind the socket to host and port thus we bind it
    # Tip: bind takes a Tuple, thus we have double brackets surrounding it
    mySocket.bind((host,port))
    # Then we call the listen method and pass the value: 1 to it so that it will perpetually listen till we close the connection
    mySocket.listen(1)
    # Then we have two variables conn and addr which will hold the connection from client and the address of the client
    conn, addr = mySocket.accept()
    # Then we print the clients address and create another variable data which is receiving data from connection
    # and we have to decode it, this step is necessary for Python 3 as normal string with str won’t pass through
    # socket and str does not implement buffer interface anymore.

    print ("Connection from: " + str(addr))
    while True:
            # We run all this in a while true loop so unless the the connection is closed
            # we run this and server’s keeps on listening when the data is received server
            # transforms in into uppercase by calling upper method and sends the string back
            # to client and we encode too as normal string will fail to transmit properly
            data = conn.recv(1024).decode()
            if not data:
                    break
            print ("from connected  user: " + str(data))
             
            data = str(data).upper()
            print ("sending: " + str(data))
            conn.send(data.encode())
             
    conn.close()
     
if __name__ == '__main__':
    Main()

    '''



, 


    '''