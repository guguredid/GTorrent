from classes.FileHandler import FileHandler
from classes.Torrent import Torrent
from classes.ClientProtocol import ClientProtocol
from classes.Client import Client
from classes.Server import Server
from Graphics import MyFrame
from generalSetting import TORRENT_SENDER_ADDRESS, FILES_ROOT
from datetime import datetime
from pubsub import pub
import win32file
import win32con
import hashlib
import threading
import socket
import sys
import shutil
import queue
import time
import os
import wx


from classes.TorrentHandlerServer import TorrentHandlerServer


def encrypt(data):
    """
    get data, return its hash
    :param data: str
    :return: str
    """
    hasher = hashlib.md5()
    hasher.update(data)
    return hasher.hexdigest()


def handle_msg_q(q):
    """
    handles the messages queue (for sending file parts)
    :param q: Queue
    :return: None
    """
    global file_server_client
    global files_in_system
    global tdata
    global tname
    global hash_list
    global DOWNLOAD_TO_ROOT
    global is_first_connection
    global my_files
    global server_client

    while True:
        ip, curr_msg = q.get()

        print(f"RECEIVE FROM {ip} MESSAGE {curr_msg}")

        code = curr_msg[:2].decode()
        info = curr_msg[2:]

        # send files to the server
        if code == '00':
            server_client.send_msg(ClientProtocol.build_send_file_names(my_files))

        # receive files from the server
        elif code == '01':
            info = info.decode()
            files_in_system = ClientProtocol.break_files_in_system(info)
            files_in_system = [file.replace('.json', '') for file in files_in_system]

            # add the files in the system to the ui
            for file in files_in_system:
                # check if already added the file to the ui (in case there was reconnection)
                if is_first_connection:
                    wx.CallAfter(pub.sendMessage, "add_file", filename=file)

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
                shutil.copyfile(upload_name, f"{FILES_ROOT}{file_name}")
                my_files.append(file_name)

                # popup that the upload succeeded
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"Uploading {file_name} has succeeded!")
            else:
                # popup that the upload succeeded
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"Uploading {file_name} has failed...")

        # receive new file that was added to the system
        elif code == '06':
            file_name = ClientProtocol.break_recv_new_file(info.decode())

            if file_name not in files_in_system:
                files_in_system.append(file_name)

            wx.CallAfter(pub.sendMessage, "add_file", filename=file_name)

        # receive torrent file
        elif code == '07':
            tdata = info.decode()

        # receive file was deleted from the server
        elif code == '09':
            file_name = ClientProtocol.break_file_deleted(info.decode())
            wx.CallAfter(pub.sendMessage, "pop_up", message=f"{file_name} WAS DELETED FROM THE SYSTEM!")
            wx.CallAfter(pub.sendMessage, "remove_file", filename=file_name)

        # asked to send file part
        elif code == '10':
            file_name, part = ClientProtocol.break_ask_part(info)
            if file_name in my_files:
                server.send_part(ip, ClientProtocol.build_send_part(file_name, part, FileHandler.get_part(f'{FILES_ROOT}{file_name}', part)))

        # receive file part
        elif code == '11':
            file_name, current_chunk, chunk = ClientProtocol.break_recv_part(curr_msg)
            if encrypt(chunk) == hash_list[current_chunk - 1]:
                # insert the chunk to the file
                FileHandler.insert_part(f'{DOWNLOAD_TO_ROOT}{tname}', chunk, current_chunk)

                if current_chunk in chunks_busy:
                    chunks_busy.remove(current_chunk)
            else:
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"Downloading {file_name} is not available at the moment...")

        # client disconnect from the sharing server
        elif code == '12':
            server.close_client(ip)

        # receive port for file socket
        elif code == '20':
            port = int(info.decode())
            file_server_client = Client(port, TORRENT_SENDER_ADDRESS, msg_q)


def handle_share(ip, id, q):
    """
    handles the connection with one sharing user
    :param ip: str
    :param id: int
    :param q: Queue
    :return: None
    """
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

            msg = ClientProtocol.build_ask_part(tname, current_chunk)
            client.send_msg(msg)
            # if the client disconnect, stop the download
        elif not client.is_running():
            break
        else:
            pass
    # client.disconnect()
    client.kill_client()


def monitor_dir():
    """
    monitors changes in the files directory, and reports them
    :return: None
    """
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

        # 1 : created file
        if results[0][0] == 1:
            msg = ClientProtocol.build_add_file(results[0][1])
        # 2 : deleted file
        elif results[0][0] == 2:
            if results[0][1] in my_files:
                my_files.remove(results[0][1])
            msg = ClientProtocol.build_send_deleted_file(results[0][1])

        # print the LOG
        if msg != '':
            server_client.send_msg(msg)


def handle_ui_events(message):
    """
    handles the events that occurs on the graphic (clicks on buttons)
    :param message: str
    :return: None
    """
    global upload_name
    global DOWNLOAD_TO_ROOT
    global FILES_ROOT
    global is_downloading
    global is_connected_to_server

    code = message[0]
    info = message[1:]

    # asked to download a file
    if code == "1":
        # check if connected to the server
        if is_connected_to_server:
            # check if not downloading already
            if not is_downloading:
                if info not in my_files:
                    threading.Thread(target=download_file, args=(info, ), daemon=True).start()
                else:
                    # if already have the file, copy it to the monitored folder
                    shutil.copyfile(f"{FILES_ROOT}{info}", f'{DOWNLOAD_TO_ROOT}{info}')
                    wx.CallAfter(pub.sendMessage, "pop_up", message=f"Copied the file to the wanted folder", flag=True)
            else:
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"Another download is occurring at the moment...")
        else:
            wx.CallAfter(pub.sendMessage, "pop_up", message=f"Not connected to the server currently...", flag=True)
    # asked to upload a file
    elif code == "2":
        upload_name = info
        # check if connected to the server
        if is_connected_to_server:
            upload_file()
        else:
            wx.CallAfter(pub.sendMessage, "pop_up", message=f"Can't upload a file, the server is down...")
    # asked to change directory
    elif code == "3":
        DOWNLOAD_TO_ROOT = f"{info}\\"


def download_file(download_name):
    """
    handles the download of a file
    :param download_name: str
    :return: None
    """
    global tdata
    global tname
    global chunks_to_write
    global chunks_busy
    global thread_list
    global hash_list
    global DOWNLOAD_TO_ROOT
    global is_downloading

    # TODO: FOR DEBUGING
    start = datetime.now()

    # change the flag - to stop downloading other files
    is_downloading = True

    server_client.send_msg(ClientProtocol.build_ask_torrent(download_name))

    # wait until receiving the torrent file
    while tdata == '~':
        print('waiting for torrent...')

    if tdata == '!':
        wx.CallAfter(pub.sendMessage, "pop_up", message=f"Downloading {download_name} is not available at the moment...", flag=True)

    elif tdata != '':
        t = Torrent(tdata)
        if not t.is_ok():
            # popup that there was a problem with the connection to the server
            wx.CallAfter(pub.sendMessage, "pop_up", message="There was an error with the torrent file...", flag=True)
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

            # create the threads for getting the file's parts
            for i in range(len(ip_list)):
                thread_list.append(
                    threading.Thread(target=handle_share, args=(ip_list[i], i + 1, msg_q,), daemon=True))
            # start all the threads and wait for all of them to finish
            for thread in thread_list:
                thread.start()
            # wait for all the threads to finish
            for thread in thread_list:
                thread.join()


            # check if the download went ok - check the whole hash
            if os.path.exists(f'{DOWNLOAD_TO_ROOT}{tname}'):
                with open(f'{DOWNLOAD_TO_ROOT}{tname}', 'rb') as file:
                    # whole_data = file.read().rstrip()
                    whole_data = file.read()

                if encrypt(whole_data) == whole_hash:
                    server_client.send_msg(ClientProtocol.build_send_finish_download(tname))
                    my_files.append(tname)

                    # copy the file to the monitored folder
                    shutil.copyfile(f'{DOWNLOAD_TO_ROOT}{tname}', f"{FILES_ROOT}{tname}")

                    # popup that the file was created
                    wx.CallAfter(pub.sendMessage, "pop_up", message=f"Downloading {tname} has succeeded!", flag=True)
                else:
                    os.remove(f'{DOWNLOAD_TO_ROOT}{tname}')
                    # popup that the download failed
                    wx.CallAfter(pub.sendMessage, "pop_up", message=f"There was an error while downloading {tname}...", flag=True)
            else:
                # popup that the download failed
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"There was an error while downloading {tname}...", flag=True)

    # change the flag - to enable downloading other files
    is_downloading = False
    # reset torrent's variables
    tdata = '~'

    # TODO: FOR DEBUGING
    end = datetime.now()

    print("DOWNLOAD TIME: ", end - start)


def upload_file():
    """
    handles the upload of a file
    :return: None
    """
    global upload_name
    global files_in_system

    only_name = upload_name.split('\\')[-1]
    # check if uploaded the file already
    if only_name not in my_files:
        # check if the path exist
        if os.path.exists(upload_name):
            # check if the file name is taken (another file with the same name exists)
            if only_name in files_in_system:
                # popup that the name is not valid
                wx.CallAfter(pub.sendMessage, "pop_up", message=f"The file name is already taken!")
            else:
                # check if the name is shorter then 10 letters
                if len(only_name) < 10:
                    with open(upload_name, 'rb') as f:
                        data = f.read()
                    if file_server_client is not None:
                        file_server_client.send_msg(ClientProtocol.build_add_file_to_system(only_name, data))
                else:
                    # popup that the name is not valid
                    wx.CallAfter(pub.sendMessage, "pop_up", message=f"The file name must be shorter then 10 characters!")
        else:
            # popup that the path is not valid
            wx.CallAfter(pub.sendMessage, "pop_up", message=f"Your file path is not valid...")
    else:
        # popup that already have the file
        wx.CallAfter(pub.sendMessage, "pop_up", message=f"You already have {only_name}...")


def disconnect_file_server():
    """
    handles case when the server is down (needs to disconnect the file server to get new one when reconnecting)
    :return: None
    """
    global file_server_client
    global is_first_connection
    global is_connected_to_server
    wx.CallAfter(pub.sendMessage, "pop_up", message=f"The server is down, trying to reconnect...")
    is_first_connection = False
    is_connected_to_server = False
    if file_server_client is not None:
        file_server_client.kill_client()
        file_server_client.stop_thread()
        # wx.CallAfter(pub.sendMessage, "stop_threads")
        file_server_client = None

def reconnection_to_server():
    """
    reconnect to the main server
    :return: None
    """
    global is_connected_to_server
    is_connected_to_server = True


pub.subscribe(handle_ui_events, "panel_listener")
pub.subscribe(disconnect_file_server, "server_down")
pub.subscribe(reconnection_to_server, "reconnection")

my_socket = socket.socket()
file_socket = socket.socket()

# create the monitored files' folder if does not exist
if not os.path.isdir(FILES_ROOT):
    os.mkdir(FILES_ROOT)

# queue for messages from all connections
msg_q = queue.Queue()

# server for sending files parts for clients
server = Server(2000, msg_q, 'files_server')
# connecting to the server, receiving port for the file socket, receive list of files in the system, send files from the monitored folder
server_client = Client(3000, TORRENT_SENDER_ADDRESS, msg_q, "main_server")

# the root we download the files to
DOWNLOAD_TO_ROOT = 'D:\\'

# flag - do we download something or not
is_downloading = False
# flag - is this connection the first one or not (was there reconnection or not)
is_first_connection = True
# flag - is the client conencted to the server or not (to know if need to handle the ui and try to send stuff to the server)
is_connected_to_server = True

file_server_client = None

files_in_system = ''

my_files = os.listdir(FILES_ROOT)
# server_client.send_msg(ClientProtocol.build_send_file_names(my_files))

tname = ''
tdata = '~'
hash_list = []

upload_name = ''
thread_list = []

chunks_to_write = []
chunks_busy = []

threading.Thread(target=handle_msg_q, args=(msg_q,), daemon=True).start()
threading.Thread(target=monitor_dir, daemon=True).start()

app = wx.App(False)
frame = MyFrame()
frame.Show()
app.MainLoop()

print("GOODBYE! :)")
