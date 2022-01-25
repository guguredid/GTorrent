'''
file for a class representing a server in the system
'''
from classes.ClientProtocol import ClientProtocol
import socket
import select
import queue
import threading

class Server:
    '''
    class representing a server in the system
    '''

    def __init__(self, port, q):
        '''
        initializing a server with a specific port and queue for messages
        :param port: int
        :param q: Queue
        '''
        self.port = port
        self.msg_q = q
        self._users = {}  # socket: ip
        self.server_socket = socket.socket()

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
                    # self._users[client] = address[1]
                    #TODO: NEED TO BE BY CURRENT SOCKET??
                    self._users[client] = address[0]
                    # print(f"ADDED TO DICT {client}:{address[0]}")
                    # receive data from existing client
                    data = ''
                    try:
                        length = client.recv(6).decode()
                        # check if there is problem/disconnect
                        if length == "":
                            self._disconnect(client)
                        else:
                            data = client.recv(int(length)).decode()
                    except Exception as e:
                        print(f"[ERROR] in main loop0000 - {str(e)}")
                        self._disconnect(client)
                    else:
                        # check if there is problem/disconnect
                        if data == "":
                            self._close_client(client)
                        # print the data we received
                        else:
                            print(f"The client send111 - {data}")
                            # put the msg into the queue for messages
                            self.msg_q.put(f"{self._get_ip_by_socket(client)};{data}")
                else:
                    # receive data from existing client
                    try:
                        length = current_socket.recv(6).decode()
                        # check if there is problem/disconnect
                        if length == "":
                            self._disconnect(current_socket)
                        else:
                            data = current_socket.recv(int(length)).decode()
                    except Exception as e:
                        print(f"[ERROR] in main loop - {str(e)}")
                        self._disconnect(current_socket)
                    else:
                        # print the data we received
                        print(f"The client send222 - {data}")
                        # put the msg into the queue for messages
                        self.msg_q.put(f"{self._get_ip_by_socket(current_socket)};{data}")

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
            print(f"SENDING - {msg}")
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
        print(f"{self._users[client_socket]} - disconnected")
        del self._users[client_socket]
        client_socket.close()
