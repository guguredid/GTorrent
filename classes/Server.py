'''
file for a class representing a server in the system
'''
from classes.ClientProtocol import ClientProtocol
from variable import general_port
import socket
import select
import threading


class Server:
    '''
    class representing a server in the system
    '''

    def __init__(self, port, q, type='main'):
        '''
        initializing a server with a specific port and queue for messages
        :param port: int
        :param q: Queue
        '''
        self.port = port
        self.msg_q = q
        self._users = {}  # socket: ip
        self.server_socket = socket.socket()
        self.type = type
        if self.type == 'main':
            self.used_ports = []

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

                    # check if the main server - if
                    if self.type == 'main':
                        # create server for sending files
                        pass

                    # receive data from existing client
                    data = ''
                    try:
                        length = client.recv(6).decode()
                        # print(f"LEN SERVER! {length}")
                        # check if there is problem/disconnect
                        if length == "":
                            self._disconnect(client)
                        else:
                            data = client.recv(int(length))
                            # data = client.recv(int(length)).decode()
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
                    print(444444, len(self._users.keys()))
                    # receive data from existing client
                    try:
                        length = current_socket.recv(6).decode()
                        # check if there is problem/disconnect
                        if length == "":
                            print("USER DISCONNECTED!!!! 222222222222222222")
                            self._disconnect(current_socket)
                        else:
                            data = current_socket.recv(int(length))
                            # data = current_socket.recv(int(length)).decode()
                    except Exception as e:
                        print(f"[ERROR] in main loop11111 - {str(e)}")
                        self._disconnect(current_socket)
                    else:
                        print(3333333, len(self._users.keys()))
                        # if the client did not disconnect, push the msg to the queue
                        if client in self._users.keys():
                            self.msg_q.put((self._get_ip_by_socket(client), data))

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
        print(f"IP - {ip}")
        # print(f"DICT: {self._users}")
        soc = None
        for user_soc, user_ip in self._users.items():
            if user_ip == ip:
                soc = user_soc
                break

        # for user_soc, x in self._users.items():
        #     print(f"CURRENT IP: {self._users[user_soc]}")
        #     if self._users[user_soc] == ip:
        #         soc = user_soc
        #         break
        print(f"SOCKET: {soc}")
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
        print(f"DICT: {self._users}")

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
        print(f"{self._users[client_socket]} - disconnected")
        del self._users[client_socket]
        client_socket.close()
