'''
file for a class representing a client in the system
'''
import socket
import threading
import queue


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
        else:
            self.running = True
            # print('--------22', self.running)
            while self.running:
                # print(f"IN CLIENT - {self.msg_to_send}")
                    #TODO: THE SOCKET IS FOR RECEIVE AND SEND AT THE SAME TIME - A PROBLEM???
                    try:
                        length = self.my_socket.recv(6).decode()
                    except Exception as e:
                        self.disconnect()
                    else:
                        if length == '':
                            self.disconnect()
                        else:
                            msg = self.my_socket.recv(int(length))
                            self.msg_q.put((self.server_ip, msg))

    def send_msg(self, msg):
        '''

        :param msg:
        :return:
        '''
        self._send_msg_q.put(msg)

    def _send_msg(self):
        '''
        sends messages from the queue to the server
        :param msg: str
        :return: None
        '''

        while True:
            if self.running:
                msg = self._send_msg_q.get()
                try:
                    self.my_socket.send(str(len(msg)).zfill(6).encode())
                    self.my_socket.send(msg.encode())
                except Exception as e:
                    self.disconnect()
                    break

    def disconnect(self):
        print("=======================DISCONNCTED")
        self.running = False
        self.my_socket.close()

