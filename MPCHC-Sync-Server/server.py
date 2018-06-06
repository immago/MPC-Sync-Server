from model import Data, State
from manager import Manager
import json
import socket
import threading
import struct

# Secret token
SECRET_TOKEN = '86de0ff4-3115-4385-b485-b5e83ae6b890'
manager = Manager()

# Debug
def callback(data: Data):
    print(data.position)

#def process(command):
    
#    # Parse
#    try:
#        responce = json.loads(msg)
#    except ValueError:
#        send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'Not valid JSON', 'code': '1'}))
#        return
        
#    # Access variables
#    if 'token' in responce:
#        token = responce['token']

#    if 'identifer' in responce:
#        identifer = responce['identifer']

#    if token is None:
#        send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'No token', 'code': '2'}))
#        return

#    if identifer is None:
#        send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'No identifer', 'code': '3'}))
#        return

#    if token != SECRET_TOKEN:
#        send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'Wrong token', 'code': '4'}))
#        return

#    if 'command' in responce:
#        command = responce['command']

#        if(command == 'subscribe'):
#            manager.subscribe(identifer, callback)

# Socket messages

def send_msg(sock, msg):
    msg = msg + '<EOF>'
    msg = msg.encode("utf-8")
    sock.sendall(msg)

# Read message length and unpack it into an integer
#def recv_msg(sock):
#    raw_msglen = recvall(sock, 4)
#    if not raw_msglen:
#        return None
#    msglen = struct.unpack('>I', raw_msglen)[0]
#    # Read the message data
#    return recvall(sock, msglen)

## Helper function to recv n bytes or return None if EOF is hit
#def recvall(sock, n):
#    data = b''
#    while len(data) < n:
#        packet = sock.recv(n - len(data))
#        if not packet:
#            return None
#        data += packet
#    return data

def recv_msg(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        
        try:
            part = sock.recv(BUFF_SIZE)
        except ValueError:
            return None

        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data.decode("utf-8")

# Client thread
def on_new_client(clientsocket, addr):
    
    identifer = None #session identifer
    token = None #access token

    #send_msg(clientsocket, 'TEST')

    while True:

        msg = recv_msg(clientsocket)

        # Check connection
        if(msg is None):
            break

        coomnds = msg.split('<EOF>')
        for command in coomnds:

            # skip empty command
            if(len(command) == 0):
                continue

            print(command)

            # Parse
            try:
                responce = json.loads(msg)
            except ValueError:
                send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'Not valid JSON', 'code': '1'}))
                continue
        
            # Access variables
            if 'token' in responce:
                token = responce['token']

            if 'identifer' in responce:
                identifer = responce['identifer']

            if token is None:
                send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'No token', 'code': '2'}))
                continue

            if identifer is None:
                send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'No identifer', 'code': '3'}))
                continue

            if token != SECRET_TOKEN:
                send_msg(clientsocket, json.dumps({'status': 'error', 'description': 'Wrong token', 'code': '4'}))
                continue


            if 'command' in responce:
                command = responce['command']

                if(command == 'subscribe'):
                    manager.subscribe(identifer, callback)
    
    clientsocket.close()

#class ThreadedServer(object):
#    def __init__(self, host, port):
#        self.host = host
#        self.port = port
#        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.sock.bind((self.host, self.port))

#    def listen(self):
#        self.sock.listen(500)
#        while True:
#            client, address = self.sock.accept()
#            client.settimeout(60)
#            threading.Thread(target = self.listenToClient, args = (client,address)).start()

#    def listenToClient(self, client, address):
#        size = 1024
#        while True:
#            try:
#                data = client.recv(size)
#                if data:
#                    # Set the response to echo back the recieved data 
#                    print(data)
#                    response = 'hello world'
#                    client.send(response)
#                else:
#                    raise error('Client disconnected')
#            except:
#                client.close()
#                return False

#if __name__ == "__main__":
#    host = socket.gethostname()
#    port = 5000
#    ThreadedServer(host, port).listen()

if __name__ == '__main__':
    #manager.set('123', Data('test.mpg', 3600, 1, State.Playing))
    #manager.subscribe('123', callback)

    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 5000                 # Reserve a port for your service.
    s.bind((host, port))        # Bind to the port

    s.listen(500)               # Now wait for client connection.

    print('Listen on ' + str(port))

    while True:
       c, addr = s.accept()     # Establish connection with client.
       #thread.start_new_thread(on_new_client,(c,addr))
       threading.Thread(target = on_new_client, args = (c,addr)).start()

    s.close()
