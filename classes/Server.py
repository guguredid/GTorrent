'''
file for a class representing a server in the system
'''
from classes.ServerProtocol import ServerProtocol
from classes.DB import DB
import threading
import socket
import select
import random


class Server:
    """
    class representing a server in the system
    """

    def __init__(self, port, q, type='main'):
        """
        initializing a server with a specific port and queue for messages
        :param port: int
        :param q: Queue
        :param type: str
        """
        self.port = port
        self.msg_q = q
        self._users = {}  # socket: ip
        self.server_socket = socket.socket()
        self.type = type
        # if this is the main server, create a list of used ports for files servers, and the database
        if self.type == 'main':
            self._used_ports = {'test': 1000}   # socket: port
            self.db = DB("GTorrent")

        threading.Thread(target=self._main_loop, daemon=True).start()

    def _main_loop(self):
        """
        running the main loop of the server
        :return: None
        """
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
                        # save the port so other clients won't use it
                        self._used_ports[client] = port
                        # send the client the port for him
                        msg = ServerProtocol.build_send_port(port)
                        self.msg_q.put((self._get_ip_by_socket(client), msg.encode()))
                        # send the client a list of the files in the server
                        self.msg_q.put((self._get_ip_by_socket(client), '99'.encode()))
                else:
                    # receive data from existing client
                    try:
                        length = current_socket.recv(10).decode()
                        # check if there is problem/disconnect
                        if length == "":
                            self._disconnect(current_socket)
                        else:
                            data = self._recv_data(current_socket, int(length))
                    except Exception as e:
                        print(f"[ERROR] in main loop11111 - {str(e)}")
                        self._disconnect(current_socket)
                    else:
                        # if the client did not disconnect, push the msg to the queue
                        if current_socket in self._users.keys():
                            self.msg_q.put((self._get_ip_by_socket(current_socket), data))

    def _recv_data(self, soc, length):
        """
        returns the data from the socket, gets in chunks of 1024
        :param soc: Socket
        :param length: int
        :return: bytes
        """
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
        """
        returns the ip according to its socket
        :param soc: Socket
        :return: str
        """
        if soc in self._users.keys():
            return self._users[soc]
        return None

    def _get_soc_by_ip(self, ip):
        """
        returns the socket according its ip
        :param ip: str
        :return: Socket
        """
        soc = None
        for user_soc, user_ip in self._users.items():
            if user_ip == ip:
                soc = user_soc
                break
        return soc

    def send_msg(self, ip, msg):
        """
        sends to the given ip the given message
        :param ip: str
        :param msg: str \ bytes
        :return: None
        """
        soc = self._get_soc_by_ip(ip)
        if soc is not None:
            if type(msg) == str:
                msg = msg.encode()
            try:
                soc.send(str(len(msg)).zfill(10).encode())
                soc.send(msg)
            except Exception as e:
                print(f'[ERROR] int send_msg - {str(e)}')
                self._disconnect(soc)
        else:
            print("SOC IS NONE!")

    def send_all(self, msg):
        """
        send the given message to all clients
        :param msg: str
        :return: None
        """
        for user_ip in self._users.values():
            threading.Thread(target=self.send_msg, args=(user_ip, msg,), daemon=True).start()

    def send_part(self, ip, msg):
        """
        sending file's part from one client to another
        send to the given ip the given message
        :param ip: str
        :param msg: bytes
        :return: None
        """
        soc = self._get_soc_by_ip(ip)
        try:
            soc.send(str(len(msg)).zfill(10).encode())
            soc.send(msg)
        except Exception as e:
            print(f'[ERROR] in send_part - {str(e)}')
            self._disconnect(soc)

    def get_ip_list(self):
        """
        return list of connected ips
        :return: list
        """
        return self._users.values()

    def close_client(self, ip):
        """
        closes the connection to the given ip
        :param ip: str
        :return: None
        """
        self._disconnect(self._get_soc_by_ip(ip))

    def _disconnect(self, client_socket):
        """
        get client socket, remove from the list and close it
        :param client_socket: Socket
        :return: None
        """
        if client_socket in self._users.keys():
            print(f"{self._users[client_socket]} - disconnected")
            del self._users[client_socket]
            if self.type == 'main':
                del self._used_ports[client_socket]
            client_socket.close()
