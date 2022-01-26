from classes.FileHandler import FileHandler
from classes.Torrent import Torrent
from classes.ClientProtocol import ClientProtocol
from classes.Client import Client
import socket
import threading
import sys
import hashlib
import queue


def encrypt(data):
    '''
    get data, return its hash
    :param data: str
    :return: str
    '''
    hasher = hashlib.md5()
    hasher.update(data)
    return hasher.hexdigest()


def handle_msg_q(q):
    '''
    handles the messages queue
    :param q: Queue
    :return: None
    '''
    while True:
        ip, curr_msg = q.get()

        code = curr_msg[:2].decode()

        if code == '11':
            file_name, current_chunk, chunk = ClientProtocol.break_recv_part(curr_msg)
            if encrypt(chunk) == hash_list[current_chunk - 1]:
                # wait until can update the file
                file_event.wait()
                # lock the thread to prevent other threads from using it
                file_event.clear()
                # insert the chunk to the file
                FileHandler.insert_part(tname, chunk, current_chunk)
                # unlock the event for next thread
                if current_chunk in chunks_busy:
                    chunks_busy.remove(current_chunk)
                file_event.set()
            else:
                print('THE HASH IS NOT OKAY!')


def handle_share(ip, id, q):
    '''
    handles the connection with one sharing user
    :param ip: str
    :param id: int
    :param q: Queue
    :return: None
    '''
    global file_event, chunks_to_write, chunks_busy, tname, hash_list, whole_hash

    current_chunk = ''
    client = Client(2000, ip, q)
    while len(chunks_to_write) > 0 or len(chunks_busy) > 0:
        if current_chunk not in chunks_busy:
            if len(chunks_to_write) > 0:
                current_chunk = chunks_to_write.pop(0)
                chunks_busy.append(current_chunk)
            elif len(chunks_busy) > 0:
                current_chunk = chunks_busy[0]
            # connect to the client - SHOULD BE HERE OR IN THE MAIN LOOP???
            try:
                #TODO: SET TIMEOUT WITH soc.settimeout(...)???
                msg = ClientProtocol.build_ask_part(tname, current_chunk)
                client.send_msg(msg)
            except TimeoutError as e:
                print('TIMEOUT!')
                break
                # disconnect
            except Exception as e:
                print(f"[ERROR] in handle_share - {str(e)} id={id}")
                break
        else:
            pass
    client.disconnect()
    print(f"THREAD {id} FINISHED!")


name = input("ENTER THE NAME OF THE FILE YOU WANT: ")

# receive the torrent file from the server first
# TORRENT_SENDER_ADDRESS = "192.168.4.83"
TORRENT_SENDER_ADDRESS = "127.0.0.1"
my_socket = socket.socket()
try:
    my_socket.connect((TORRENT_SENDER_ADDRESS, 3000))
    msg = ClientProtocol.build_ask_torrent(name)
    my_socket.send(f"{str(len(msg)).zfill(6)}{msg}".encode())
    msg = my_socket.recv(int(my_socket.recv(6).decode())).decode()
    tdata = msg[2:]
except Exception as e:
    sys.exit('[ERROR] in connecting to server')

t = Torrent(tdata)
# data from the torrent file
tname = t.get_name().replace('.torrent', '')
hash_list = t.get_parts_hash()
chunks_num = len(hash_list)
whole_hash = t.get_hash()
ip_list = t.get_ip_list()

# list of the chunks still needed
chunks_to_write = [i for i in range(1, chunks_num+1)]
# list of the chunks being taken care of
chunks_busy = []
# event object
file_event = threading.Event()
file_event.set()

msg_q = queue.Queue()

threading.Thread(target=handle_msg_q, args=(msg_q,), daemon=True).start()

# list of the threads building the file
thread_list = []
# create the threads for getting the file's parts
for i in range(len(ip_list)):
    thread_list.append(threading.Thread(target=handle_share, args=(ip_list[i], i+1, msg_q,)))

for thread in thread_list:
    thread.start()
# wait for all the threads to finish
for thread in thread_list:
    thread.join()

print("all finished!")

# check the whole hash
with open(f'{tname}', 'rb') as file:
    whole_data = file.read()
if encrypt(whole_data) == whole_hash:
    print('THE FILE IS OK!')
else:
    print('THE FILE IS NOT OK!')
