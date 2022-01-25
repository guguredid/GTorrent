from classes.FileHandler import FileHandler
from classes.Torrent import Torrent
from classes.ClientProtocol import ClientProtocol
from classes.Client import Client
import socket
import threading
import sys
import ast
import hashlib
import time
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

        # print(f"WHOLE MESSAGE - {msg}, {msg[:2]}")
        # print(f"RECEIVED FROM {ip} - {curr_msg} - CODE={curr_msg[:2].decode()}, {len(curr_msg)}")

        code = curr_msg[:2].decode()

        if code == '11':
            file_name, current_chunk, chunk = ClientProtocol.break_recv_part(curr_msg)
            # file_name = msg[2:12].decode().rstrip()
            # current_chunk = int(bytes(msg[12:16]).decode())
            # chunk = bytes(msg[16:])
            # print(f"CODE - {code}, NAME - {file_name}, CURRENT CHUNK - {current_chunk}, CHUNK - {chunk}, LEN - {len(chunk)}")
            # check if the chunk's hash is correct (if the data is ok)
            if encrypt(chunk) == hash_list[current_chunk - 1]:
                # print("INSERT TO FILE")
                # wait until can update the file
                file_event.wait()
                # lock the thread to prevent other threads from using it
                file_event.clear()
                # insert the chunk to the file
                FileHandler.insert_part(tname, chunk, current_chunk)
                # unlock the event for next thread
                if current_chunk in chunks_busy:
                    # print('REMOVING!')
                    chunks_busy.remove(current_chunk)
                file_event.set()


def handle_share(ip, id, q):
    '''
    handles the connection with one sharing user
    :param soc: Socket
    :param q: Queue
    :return: None
    '''
    global file_event, chunks_to_write, chunks_busy, tname, hash_list, whole_hash
    # soc = socket.socket()
    # soc.settimeout(10.0) # 10 seconds
    # try:
    #     soc.connect((ip, 2000))
    # except Exception as e:
    #     print(f"ERROR! {str(e)}")
    # else:
    current_chunk = ''
    client = Client(2000, ip, q)
    while len(chunks_to_write) > 0 or len(chunks_busy) > 0:
        # print('STILL RUNNING: ', len(chunks_to_write), len(chunks_busy))
        #TODO: THINK OF A WAY THE THREAD WILL WAIT UNTIL ITS CHUNK IS FINISHED AND ONLY THEN SEND ANOTHER MESSAGE THROUGH THE CLIENT
        if current_chunk not in chunks_busy:
            if len(chunks_to_write) > 0:
                current_chunk = chunks_to_write.pop(0)
                # chunks_to_write.remove(current_chunk)
                chunks_busy.append(current_chunk)
            elif len(chunks_busy) > 0:
                current_chunk = chunks_busy[0]
            # print(f'CORRENT CHUNK:{current_chunk} id={id}')
            # connect to the client - SHOULD BE HERE OR IN THE MAIN LOOP???
            try:
                #TODO: SET TIMEOUT WITH soc.settimeout(...)???
                msg = ClientProtocol.build_ask_part(tname, current_chunk)
                client.send_msg(msg)
                # soc.send(str(len(msg)).zfill(6).encode())
                # soc.send(msg.encode())
                # chunk = soc.recv(int(soc.recv(6).decode()))

            except TimeoutError as e:
                print('TIMEOUT!')
                break
                # disconnect
            except Exception as e:
                print(f"[ERROR] in handle_share - {str(e)} id={id}")
                break
            else:
                pass
        else:
            pass
            # print(f"THREAD {id} - STILL HANDELING MY PART!")
            # code = chunk[:2].decode()
            # file_name = chunk[2:12].decode().rstrip()
            # chunk = chunk[12:]
            # # print(f"CODE - {code}, NAME - {file_name}, CHUNK - {chunk}")
            # # check if the chunk's hash is correct (if the data is ok)
            # if encrypt(chunk) == hash_list[current_chunk-1]:
            #     # print("INSERT TO FILE")
            #     # wait until can update the file
            #     file_event.wait()
            #     # lock the thread to prevent other threads from using it
            #     file_event.clear()
            #     # insert the chunk to the file
            #     FileHandler.insert_part(tname, chunk, current_chunk)
            #     # unlock the event for next thread
            #     if current_chunk in chunks_busy:
            #         # print('REMOVING!')
            #         chunks_busy.remove(current_chunk)
            #     file_event.set()
    client.disconnect()
    print(f"THREAD {id} FINISHED!")


# receive the torrent file from the server first
# TORRENT_SENDER_ADDRESS = "192.168.4.83"
TORRENT_SENDER_ADDRESS = "127.0.0.1"
my_socket = socket.socket()
try:
    my_socket.connect((TORRENT_SENDER_ADDRESS, 3000))
    msg = ClientProtocol.build_ask_torrent('dog.jpg')
    my_socket.send(f"{str(len(msg)).zfill(6)}{msg}".encode())
    msg = my_socket.recv(int(my_socket.recv(6).decode())).decode()
    tdata = msg[2:]
except Exception as e:
    sys.exit('[ERROR] in connecting to server')

# print(f"TDATA - {tdata}")

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

#
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

#TODO: DOES NOT WORK WELL

# check the whole hash
with open(f'{tname}', 'rb') as file:
    whole_data = file.read()

# pad the last chunk to be 1024
print(f"WHOLE DATA {len(whole_data)}, ")
if len(whole_data) % 1024 != 0:
    to_add = (' ' * (1024 - (len(whole_data) % 1024))).encode()
    print(f"LEN- {len(whole_data)}, {len(to_add)}")
    whole_data += to_add
print('WHOLE HASH', whole_hash)
print('CURRENT HASH', encrypt(whole_data))
if encrypt(whole_data) == whole_hash:
    print('THE FILE IS OK!')
else:
    print('THE FILE IS NOT OK!')
