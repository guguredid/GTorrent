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
        # flag - the clients runs or not
        self.running = False
        # flag - the object still running
        self.thread_running = True

        # start the threads responsible for connection with the server
        threading.Thread(target=self._main_loop, args=()).start()
        time.sleep(1)
        threading.Thread(target=self._send_msg, args=()).start()

    def _main_loop(self):
        '''
        initializing the socket and waits for messages
        :return: None
        '''

        # while self.thread_running:
        while True:
            # first connection / try to reconnect if disconnection occurs
            try:
                self.my_socket.connect((self.server_ip, self.server_port))
            except Exception as e:
                print(f"[ERROR] in main loop1 - {str(e)}")
                self.disconnect()
            else:
                self.running = True
                print("CLIENTTTTTTT", self.running)
                while self.running:
                # while True:
                    try:
                        length = int(self.my_socket.recv(10).decode())
                    except Exception as e:
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
        # loops and receive the data in chunks of 1024
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
        puts the given message into the _send_msg_q
        :param msg: str\bytes
        :return:
        '''
        self._send_msg_q.put(msg)

    def _send_msg(self):
        '''
        sends messages from the queue to the server
        :return: None
        '''

        # while self.thread_running:
        while True:
            if self.running:
                msg = self._send_msg_q.get()
                if type(msg) is str:
                    msg = msg.encode()
                try:
                    self.my_socket.send(str(len(msg)).zfill(10).encode())
                    self.my_socket.send(msg)
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
        print("=======================DISCONNECTED")
        self.running = False
        # self.thread_running = False
        self.my_socket.close()

    def kill_client(self):
        '''
        disconnects from the server and kills all threads
        :return: None
        '''
        threads = threading.get_ident()


