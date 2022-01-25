from classes.FileHandler import FileHandler
from classes.Torrent import Torrent
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


def handle_share(ip, id):
    '''
    handles the connection with one sharing user
    :param soc: Socket
    :return: None
    '''
    global file_event, chunks_to_write, chunks_busy, tname, hash_list, whole_hash
    soc = socket.socket()
    try:
        soc.connect((ip, 2000))
    except Exception as e:
        print(f"ERROR! {str(e)}")
    else:
        while len(chunks_to_write) > 0 or len(chunks_busy) > 0:
            print('STILL RUNNING: ', len(chunks_to_write), len(chunks_busy))
            if len(chunks_to_write) > 0:
                current_chunk = chunks_to_write.pop(0)
                # chunks_to_write.remove(current_chunk)
                chunks_busy.append(current_chunk)
                print(f'CORRENT CHUNK:{current_chunk} id={id}')
            # connect to the client - SHOULD BE HERE OR IN THE MAIN LOOP???
            try:
                #TODO: SET TIMEOUT WITH soc.settimeout(...)???
                soc.send(f"{current_chunk}".zfill(4).encode())
                chunk = soc.recv(1024)
            except Exception as e:
                print(f"[ERROR] in handle_share - {str(e)} id={id}")
                break
            else:
                # check if the chunk's hash is correct (if the data is ok)
                if encrypt(chunk) == hash_list[current_chunk-1]:
                    # wait until can update the file
                    file_event.wait()
                    # lock the thread to prevent other threads from using it
                    file_event.clear()
                    # insert the chunk to the file
                    FileHandler.insert_part(tname, chunk, current_chunk)
                    # unlock the event for next thread
                    if current_chunk in chunks_busy:
                        print('REMOVING!')
                        chunks_busy.remove(current_chunk)
                    file_event.set()
                    # if current_chunk in chunks_busy:
                    #     print('REMOVING!')
                    #     chunks_busy.remove(current_chunk)
    soc.close()


# receive the torrent file from the server first
TORRENT_SENDER_ADDRESS = "192.168.4.83"
my_socket = socket.socket()
try:
    my_socket.connect((TORRENT_SENDER_ADDRESS, 3000))
    my_socket.send('dog.jpg'.ljust(10).encode())
    tdata = my_socket.recv(int(my_socket.recv(5).decode())).decode()
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

thread_list = []
# create the threads for getting the file's parts
for i in range(len(ip_list)):
    thread_list.append(threading.Thread(target=handle_share, args=(ip_list[i], i+1)))

print(len(thread_list))
for thread in thread_list:
    thread.start()
# wait for all the threads to finish
for thread in thread_list:
    thread.join()

print("all finished!")

# check the whole hash
with open(f'{tname}', 'rb') as file:
    whole_data = file.read()
print('WHOLE HASH', whole_hash)
print('CURRENT HASH', encrypt(whole_data))
if encrypt(whole_data) == whole_hash:
    print('THE FILE IS OK!')
else:
    print('THE FILE IS NOT OK!')
