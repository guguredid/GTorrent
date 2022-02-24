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
    global file_server_client
    global files_in_system
    global tdata

    while True:
        ip, curr_msg = q.get()

        code = curr_msg[:2].decode()
        info = curr_msg[2:]

        # receive files from the server
        if code == '01':
            info = info.decode()
            files_in_system = ClientProtocol.break_files_in_system(info)
            files_in_system = [file.replace('.json', '') for file in files_in_system]

        # delete a file from the monitored folder
        elif code == '02':
            file_name = ClientProtocol.break_delete_file(info.decode())
            if os.path.exists(f"{FILES_ROOT}{file_name}"):
                os.remove(f"{FILES_ROOT}{file_name}")

        # receive the uploaded file's status (managed to upload or not)
        elif code == '05':
            info = info.decode()
            file_name, status = ClientProtocol.break_added_status(info)
            # if the file is added to the system, write it to the monitored folder
            if status == '1':
                print("FILE ADDED SUCCESSFULLY!")
                shutil.copyfile(upload_name, f"{FILES_ROOT}{file_name}")
                my_files.append(file_name)
            else:
                print("FILE WAS NOT ADDED")

        # receive new file that was added to the system
        elif code == '06':
            file_name = ClientProtocol.break_recv_new_file(info.decode())
            print(f"NEW FILE ADDED TO THE SYSTEM: {file_name}")
            if file_name not in files_in_system:
                files_in_system.append(file_name)

        # receive torrent file
        elif code == '07':
            tdata = info.decode()

        # receive an update about ip address (for downloading)
        elif code == '08':
            ip, status = ClientProtocol.break_update_ip(info.decode())
            print(f"RECEIVED UPDATE FOR {ip}======{status}")
            # check if the ip is sharing or stopped sharing
            if status == 1:
                print(f"{ip} CAN NOW SHARE THE FILE WE NEED!")
                thread_list.append(threading.Thread(target=handle_share, args=(ip, len(thread_list)+1, msg_q)))
                thread_list[-1].start()
                thread_list[-1].join()
            elif status == 0:
                print(f"{ip} STOPPED SHARING THE FILE WE NEED!")
                pass

        # asked to send file part
        elif code == '10':
            file_name, part = ClientProtocol.break_ask_part(info)
            if file_name in my_files:
                server.send_part(ip, ClientProtocol.build_send_part(file_name, part, FileHandler.get_part(f'{FILES_ROOT}{file_name}', part)))

        # receive file part
        elif code == '11':
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

        # client disconnect from the sharing server
        elif code == '12':
            server.close_client(ip)

        # receive port for file socket
        elif code == '20':
            port = int(info.decode())
            file_server_client = Client(port, TORRENT_SENDER_ADDRESS, msg_q)


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

    print(f"CONNECTING TO {ip}")

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
    # client.send_msg(ClientProtocol.build_disconnect())
    client.disconnect()
    print(f"THREAD {id} FINISHED!")


def monitor_dir():
    '''
    monitors changes in the files directory, and reports them
    :return: None
    '''
    global tname
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

        msg = ''

        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY |
            # NEW
            win32con.FILE_NOTIFY_CHANGE_SIZE,
            None,
            None
        )

        #TODO: SEND THE SERVER WHEN FINISH DOWNLOADING A FILE BY CLOSING IT???

        # 1 : created file
        #TODO: DO I NEED CREATE? IS IT OK TO LEAVE A EMPTY FILE, AND UPDATE THE SERVER ONLY WHEN THE SIZE IS CHANGING?
        if results[0][0] == 1:
            # print(f' - Created file - {results[0][1]}')
            # # if a different file then the one we're downloading is created - report it
            # if tname != results[0][1]:
            #     msg = ClientProtocol.build_add_file(results[0][1])



            print(f' - Created file - {results[0][1]}')
            msg = ClientProtocol.build_add_file(results[0][1])
        # 2 : deleted file
        elif results[0][0] == 2:
            print(f' - Deleted file - {results[0][1]}')
            msg = ClientProtocol.build_send_deleted_file(results[0][1])
        # 3: resize a file
        # elif results[0][0] == 3:
        #     print(f' - resize file - {results[0][1]}')
        #     # if the download is over, that's when we send the server the message
        #     if finish_download:
        #         msg = ClientProtocol.build_add_file(results[0][1])

        # print the LOG
        if msg != '':
            print(f"SENDING TO SERVER MONITOR!! {msg}")
            server_client.send_msg(msg)


# TORRENT_SENDER_ADDRESS = "192.168.4.74"

TORRENT_SENDER_ADDRESS = "192.168.4.83"
# TORRENT_SENDER_ADDRESS = "192.168.4.93"
# TORRENT_SENDER_ADDRESS = "192.168.4.91"
# TORRENT_SENDER_ADDRESS = "192.168.4.85"
# TORRENT_SENDER_ADDRESS = "127.0.0.1"
my_socket = socket.socket()
file_socket = socket.socket()

FILES_ROOT = 'D:\GTorrent\\'
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
# connecting to the server, receiving port for the file socket, receive list of files in the system, send files from the monitored folder
server_client = Client(3000, TORRENT_SENDER_ADDRESS, msg_q)

file_server_client = None

files_in_system = ''

my_files = os.listdir(FILES_ROOT)
print("THE FILES I HAVE::: ", my_files)
server_client.send_msg(ClientProtocol.build_send_file_names(my_files))

tname = ''
finish_download = False

# main loop
while True:
    action = input('Enter what you want to do: enter U for uploading a file, or D for downloading one. Enter exit to leave the system: ')

    if action.lower() == 'u':
        # wait until received filename with len <= 10
        not_ok = True
        while not_ok:
            upload_name = input("enter the name of the file you want, please enter a file with name 10 characters long, or less: ")
            only_name = upload_name.split('\\')[-1]
            not_ok = len(only_name) > 10
        print(f"THE FILE NAME ONLY IS ", upload_name.split('\\')[-1])
        with open(upload_name, 'rb') as f:
            data = f.read()
        if file_server_client is not None:
            file_server_client.send_msg(ClientProtocol.build_add_file_to_system(only_name, data))

    elif action.lower() == 'd':
        if len(files_in_system) > 0:
            tdata = '~'
            print(f"The files currently available are: {', '.join(files_in_system)}")
            download_name = input('Enter the name of the file you want to download: ')
            # msg = ClientProtocol.build_ask_torrent(download_name)
            server_client.send_msg(ClientProtocol.build_ask_torrent(download_name))

            # wait until receiving the torrent file
            while tdata == '~':
                print('waiting for torrent...')

            if tdata == '!':
                print("Downloading the file is not available at the moment...")

            elif tdata != '':
                print(f"RECEIVED TDATA {tdata}====={len(tdata)}")
                t = Torrent(tdata)
                if not t.is_ok():
                    print("There was an error with the torrent file...")
                else:
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

                    # flag - so the monitored won't send the server until we finish downloading the file
                    finish_download = False

                    # create the threads for getting the file's parts
                    for i in range(len(ip_list)):
                        thread_list.append(threading.Thread(target=handle_share, args=(ip_list[i], i + 1, msg_q,), daemon=True))
                    # start all the threads and wait for all of them to finish
                    for thread in thread_list:
                        thread.start()
                    # wait for all the threads to finish
                    for thread in thread_list:
                        thread.join()

                    finish_download = True

                    # check the whole hash
                    with open(f'{FILES_ROOT}{tname}', 'rb') as file:
                        whole_data = file.read().rstrip()
                    if encrypt(whole_data) == whole_hash:
                        print('THE FILE IS OK!')
                        server_client.send_msg(ClientProtocol.build_send_finish_download(tname))
                    else:
                        print('THE FILE IS NOT OK!')
            else:
                print('There is no such file in the server!')
        else:
            print("There are no available files currently...")

    elif action.lower() == 'exit':
        break

print("GOODBYE! :)")
