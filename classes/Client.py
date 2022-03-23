'''
file for a class representing a client in the system
'''
import socket
import threading
import queue
import time


class Client:
    '''
    class representing a client in the system
    '''

    def __init__(self, server_port, server_ip, recv_q):
        '''
        initializing a client object
        :param server_port: str
        :param server_ip: str
        :param recv_q: Queue
        '''
        self.msg_q = recv_q
        self._send_msg_q = queue.Queue()
        self.server_port = server_port
        self.server_ip = server_ip
        self.my_socket = socket.socket()

        self.running = False

        threading.Thread(target=self._main_loop).start()
        time.sleep(1)
        threading.Thread(target=self._send_msg).start()

    def _main_loop(self):
        '''
        initializing the socket and waits for messages
        :return: None
        '''
        #TODO: WHAT DO I DO IF THE SERVER IS DOWN??
        try:
            self.my_socket.connect((self.server_ip, self.server_port))
        except Exception as e:
            print(f"[ERROR] in main loop1 - {str(e)}")
            self.disconnect()
        else:
            self.running = True
            while self.running:
                try:
                    length = int(self.my_socket.recv(10).decode())
                except Exception as e:
                    print(111111111)
                    self.disconnect()
                else:
                    if length == '':
                        self.disconnect()
                    else:
                        try:
                            msg = self._recv_data(length)
                        except Exception as e:
                            print(f"ERROR IN CLIENT22222 -  {str(e)}")
                            self.disconnect()
                        else:
                            self.msg_q.put((self.server_ip, msg))
            print("MAIN LOOP STOPPED!!!")

    def _recv_data(self, length):
        '''
        returns the data from the socket, gets in chunks of 1024
        :param length: int
        :return: bytes
        '''
        data = bytearray()
        while len(data) < length:
            slice = length - len(data)
            if slice > 1024:
                data.extend(self.my_socket.recv(1024))
            else:
                data.extend(self.my_socket.recv(slice))
                break
        return bytes(data)

    def send_msg(self, msg):
        '''
        :param msg: str\bytes
        :return:
        '''
        self._send_msg_q.put(msg)

    def _send_msg(self):
        '''
        sends messages from the queue to the server
        :return: None
        '''

        while True:
            if self.running:
                msg = self._send_msg_q.get()
                try:
                    self.my_socket.send(str(len(msg)).zfill(10).encode())
                    if type(msg) is bytes:
                        self.my_socket.send(msg)
                    else:
                        self.my_socket.send(msg.encode())
                except Exception as e:
                    print(f'ERROR IN CLIENT! {str(e)}')
                    self.disconnect()
                    break
                else:
                    print(f"SENT TO SERVER: {self.server_ip}", msg)

    def is_running(self):
        '''
        return if the client still running or not
        :return: bool
        '''
        return self.running

    def disconnect(self):
        '''
        disconnects from the server
        :return: None
        '''
        print("=======================DISCONNCTED")
        self.running = False
        self.my_socket.close()

