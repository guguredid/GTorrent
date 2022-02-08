'''
file for a class representing a server in the system
'''
from classes.ClientProtocol import ClientProtocol
from classes.ServerProtocol import ServerProtocol
from classes.DB import DB
import socket
import select
import threading
import random


class Server:
    '''
    class representing a server in the system
    '''

    def __init__(self, port, q, type='main'):
        '''
        initializing a server with a specific port and queue for messages
        :param port: int
        :param q: Queue
        :param type: str
        '''
        self.port = port
        self.msg_q = q
        self._users = {}  # socket: ip
        self.server_socket = socket.socket()
        self.type = type
        # if this is the main server, create a list of used ports for files servers
        if self.type == 'main':
            self._used_ports = {'test': 1000}   # socket: port
            self.db = DB("GTorrent")

        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        '''
        running the main loop of the server
        :return: None
        '''
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(3)

        while True:
            rlist, wlist, xlist = select.select(list(self._users.keys()) + [self.server_socket], list(self._users.keys()), [],
                                                0.3)
            # run on the list we read from
            for current_socket in rlist:
                # check if there is a new client
                if current_socket is self.server_socket:
                    client, address = self.server_socket.accept()
                    print(f'{address[0]} - connected')
                    self._users[client] = address[0]

                    # check if the main server
                    if self.type == 'main':
                        # generate port for sending files' server for the client
                        port = 1000
                        while port in self._used_ports.values():
                            port = random.randint(2001, 2101)
                        self._used_ports[client] = port
                        msg = ServerProtocol.build_send_port(port)
                        self.msg_q.put((self._get_ip_by_socket(client), msg.encode()))
                        # send the client a list of the files in the server
                        self.msg_q.put((self._get_ip_by_socket(client), '99'.encode()))
                        #TODO: FIX GETTING THE FILES FROM THE CLIENT!
                        client_files = client.recv(int(client.recv(6).decode())).decode()[2:]
                        print(f"FILES THE CLIENT HAS: {client_files}")
                        self.msg_q.put((self._get_ip_by_socket(client), f'01{client_files}'.encode()))

                    else:
                        # receive data from existing client
                        data = ''
                        try:
                            length = client.recv(6).decode()
                            # check if there is problem/disconnect
                            if length == "":
                                self._disconnect(client)
                            else:
                                data = self.recv_data(client, int(length))
                        except Exception as e:
                            print(f"[ERROR] in main loop0000 - {str(e)}")
                            self._disconnect(client)
                        else:
                            # check if there is problem/disconnect
                            if data == "":
                                self._disconnect(client)
                            # push the data we received to the queue
                            else:
                                self.msg_q.put((self._get_ip_by_socket(client), data))
                else:
                    # receive data from existing client
                    try:
                        length = current_socket.recv(6).decode()
                        # check if there is problem/disconnect
                        if length == "":
                            self._disconnect(current_socket)
                        else:
                            data = self.recv_data(client, int(length))
                            # data = current_socket.recv(int(length)).decode()
                    except Exception as e:
                        print(f"[ERROR] in main loop11111 - {str(e)}")
                        self._disconnect(current_socket)
                    else:
                        # if the client did not disconnect, push the msg to the queue
                        if client in self._users.keys():
                            self.msg_q.put((self._get_ip_by_socket(client), data))

    def recv_data(self, soc, length):
        '''
        returns the data from the socket, gets in chunks of 1024
        :param soc: Socket
        :param len: int
        :return: bytes
        '''
        data = bytearray()
        while len(data) < length:
            slice = length - len(data)
            if slice > 1024:
                data.extend(soc.recv(1024))
            else:
                data.extend(soc.recv(slice))
                break
        return bytes(data)

    def _get_ip_by_socket(self, soc):
        '''
        returns the ip according to its socket
        :param soc: Socket
        :return: str
        '''
        return self._users[soc]

    def _get_soc_by_ip(self, ip):
        '''
        returns the socket according its ip
        :param ip: str
        :return: Socket
        '''
        soc = None
        for user_soc, user_ip in self._users.items():
            if user_ip == ip:
                soc = user_soc
                break
        return soc

    def recv_file(self, client_soc):
        '''
        receives a file from the client, saves it and adds to the message queue a note about the file
        :param client_soc: Socket
        :return: None
        '''
        # receive the file data (name, len)

        # receive the file and save it in a specific place

        # add a message about it in the message queue
        pass

    def send_msg(self, ip, msg):
        '''
        sends to the given ip the given message
        :param ip: str
        :param msg: str
        :return: None
        '''
        soc = self._get_soc_by_ip(ip)
        try:
            soc.send(str(len(msg)).zfill(6).encode())
            soc.send(msg.encode())
        except Exception as e:
            print(f'[ERROR] int send_msg - {str(e)}')
            self._disconnect(soc)

    def send_file(self, ip, msg):
        '''
        send to the given ip the given message
        :param ip: str
        :param msg: str
        :return: None
        '''
        pass

    def send_part(self, ip, msg):
        '''
        sending file's part from one client to another
        send to the given ip the given message
        :param ip: str
        :param msg: bytes
        :return: None
        '''
        soc = self._get_soc_by_ip(ip)
        try:
            soc.send(str(len(msg)).zfill(6).encode())
            soc.send(msg)
        except Exception as e:
            print(f'[ERROR] int send_part - {str(e)}')
            self._disconnect(soc)

    def _disconnect(self, client_socket):
        '''
        get client socket, remove from the list and close it
        :param client_socket: Socket
        :return: None
        '''
        # if client_socket in self._users.keys():
        #     print(f"{self._users[client_socket]} - disconnected")
        #     del self._users[client_socket]
        #     if self.type == 'main':
        #         del self._used_ports[client_socket]
        #     client_socket.close()

        print(f"{self._users[client_socket]} - disconnected")
        del self._users[client_socket]
        if self.type == 'main':
            del self._used_ports[client_socket]
        client_socket.close()
