from classes.FileHandler import FileHandler
from classes.Torrent import Torrent
from classes.ClientProtocol import ClientProtocol
from classes.Client import Client
from classes.Server import Server
import socket
import threading
import sys
import hashlib
import queue
import os
import win32file
import win32con
import shutil


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
    handles the messages queue (for sending file parts)
    :param q: Queue
    :return: None
    '''
    while True:
        ip, curr_msg = q.get()

        code = curr_msg[:2].decode()
        info = curr_msg[2:]

        # delete a file from the monitored folder
        if code == '02':
            print(f"DELETING {info} FROM THE MONITORED FOLDER!")
            if os.path.exists(f"{FILES_ROOT}{info}"):
                os.remove(f"{FILES_ROOT}{info}")

        # asked to send file part
        if code == '10':
            file_name, part = ClientProtocol.break_ask_part(info)
            server.send_part(ip, ClientProtocol.build_send_part(file_name, part, FileHandler.get_part(f'{FILES_ROOT}{file_name}', part)))

        # receive file part
        if code == '11':
            file_name, current_chunk, chunk = ClientProtocol.break_recv_part(curr_msg)
            if encrypt(chunk) == hash_list[current_chunk - 1]:
                # wait until can update the file
                file_event.wait()
                # lock the thread to prevent other threads from using it
                file_event.clear()
                # insert the chunk to the file
                FileHandler.insert_part(f'{FILES_ROOT}{tname}', chunk, current_chunk)
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


def monitor_dir():
    '''
    monitors changes in the files directory, and reports them
    :return: None
    '''
    hDir = win32file.CreateFile(
        FILES_ROOT,
        win32con.FILE_SHARE_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    # monitor the directory
    while True:

        new_log = ''

        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
        )

        # 1 : created file
        if results[0][0] == 1:
            new_log = f' - Created file - {results[0][1]}\n'
            msg = ClientProtocol.build_add_file(results[0][1])
        # 2 : deleted file
        elif results[0][0] == 2:
            new_log = f' - Deleted file - {results[0][1]}\n'
            msg = ClientProtocol.build_send_deleted_file(results[0][1])

        # print the LOG
        if new_log != '':
            print(new_log, end='')
            print(msg)


TORRENT_SENDER_ADDRESS = "192.168.4.74"
# TORRENT_SENDER_ADDRESS = "192.168.4.83"
# TORRENT_SENDER_ADDRESS = "192.168.4.93"
# TORRENT_SENDER_ADDRESS = "192.168.4.85"
# TORRENT_SENDER_ADDRESS = "127.0.0.1"
my_socket = socket.socket()
file_socket = socket.socket()

FILES_ROOT = 'C:\GTorrent\\'
# create the files' folder if does not exist
if not os.path.isdir(FILES_ROOT):
    os.mkdir(FILES_ROOT)

# event object
file_event = threading.Event()
file_event.set()
# queue for messages from all connections
msg_q = queue.Queue()

threading.Thread(target=handle_msg_q, args=(msg_q,), daemon=True).start()
threading.Thread(target=monitor_dir, daemon=True).start()

# server for sending files parts for clients
server = Server(2000, msg_q, 'files_server')

action = input('Enter what you want to do: enter U for uploading a file, or D for downloading one ')

# connect the sockets to the server (1 for messages, 1 for sending files
try:
    my_socket.connect((TORRENT_SENDER_ADDRESS, 3000))
    # receive port for the file's server
    file_port = int(my_socket.recv(int(my_socket.recv(6).decode())).decode())
    file_socket.connect((TORRENT_SENDER_ADDRESS, file_port))
    # receive list of files in the system
    files_in_system = my_socket.recv(int(my_socket.recv(6).decode())).decode()
    files_in_system = ClientProtocol.break_files_in_system(files_in_system)
    # send the files in the monitored folder
    my_files = os.listdir(FILES_ROOT)
    msg = ClientProtocol.build_send_file_names(my_files)
    my_socket.send(str(len(msg)).zfill(6).encode())
    my_socket.send(msg.encode())
except Exception as e:
    sys.exit('[ERROR] in connecting to server')

if action.lower() == 'u':
    upload_name = input("enter the name of the file you want: ")
    only_name = upload_name.split('\\')[-1]
    # print(f"THE FILE NAME ONLY IS {upload_name.split('\\')[-1]}")
    with open(upload_name, 'rb') as f:
        data = f.read()

    try:
        msg = ClientProtocol.build_add_file_to_system(only_name, data)
        file_socket.send(f"{str(len(msg)).zfill(6)}".encode())
        file_socket.send(msg)
        answer = file_socket.recv(int(file_socket.recv(6).decode())).decode()
    except Exception as e:
        sys.exit('[ERROR] in connecting to server')
    else:
        code = answer[:2]
        info = answer[2:]
        if code == '05':
            file_name, status = ClientProtocol.break_added_status(info)
            # if the file is added to the system, write it to the monitored folder
            if status == '1':
                print("FILE ADDED SUCCESSFULLY!")
                shutil.copyfile(upload_name, f"{FILES_ROOT}{only_name}")
            else:
                print("FILE WAS NOT ADDED")

elif action.lower() == 'd':
    files_in_system = [file.replace('.json', '') for file in files_in_system]
    if len(files_in_system) == 0:
        print("Sorry, it appears there are no available files to download from the system...")
    else:
        print(f"The files available in the system: {', '.join(files_in_system)}")
        download_name = input('Enter the name of the file you want to download: ')

        try:
            msg = ClientProtocol.build_ask_torrent(download_name)
            my_socket.send(f"{str(len(msg)).zfill(6)}{msg}".encode())
            msg = my_socket.recv(int(my_socket.recv(6).decode())).decode()
            tdata = msg[2:]
        except Exception as e:
            sys.exit('[ERROR] in connecting to server')
        else:
            if tdata != '':
                t = Torrent(tdata)
                # data from the torrent file
                tname = t.get_name().replace('.torrent', '')

                hash_list = t.get_parts_hash()
                chunks_num = len(hash_list)
                whole_hash = t.get_hash()
                ip_list = t.get_ip_list()

                # list of the chunks still needed
                chunks_to_write = [i for i in range(1, chunks_num + 1)]
                # list of the chunks being taken care of
                chunks_busy = []
                # list of the threads building the file
                thread_list = []

                # create the threads for getting the file's parts
                for i in range(len(ip_list)):
                    thread_list.append(threading.Thread(target=handle_share, args=(ip_list[i], i + 1, msg_q,), daemon=True))
                # start all the threads and wait for all of them to finish
                for thread in thread_list:
                    thread.start()
                # wait for all the threads to finish
                for thread in thread_list:
                    thread.join()

                # check the whole hash
                with open(f'{FILES_ROOT}{tname}', 'rb') as file:
                    whole_data = file.read().rstrip()
                if encrypt(whole_data) == whole_hash:
                    print('THE FILE IS OK!')
                else:
                    print('THE FILE IS NOT OK!')
            else:
                print('There is no such file in the server!')
