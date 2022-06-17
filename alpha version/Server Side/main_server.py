from classes.DB import DB
from classes.Server import Server
from classes.ServerProtocol import ServerProtocol
from classes.TorrentHandlerServer import TorrentHandlerServer
import queue
import os
import threading
import json


def handle_files(q):
    """
    handles the queue for uploading files to the system.
    :param q: Queue
    :return: None
    """
    global server_by_ip
    local_db = DB("GTorrent")
    while True:
        ip, data = q.get()

        code = data[:2]
        info = data[2:]

        # receive new file to the system
        if code == '05'.encode():
            # receive new file
            f_name, data = ServerProtocol.break_recv_file(info)

            print(f"RECEIVED FILE {f_name} FROM {ip} AND THE DATA {len(data)}")

            # save temporarily and create json file to it
            with open(f"temp{f_name}", 'wb') as f:
                f.write(data)
            temp_torrent = TorrentHandlerServer.build_torrent(f"temp{f_name}", ip)
            with open(f'{TORRENT_ROOT}{f_name}.json', 'w') as file:
                file.write(temp_torrent)

            # update if managed to do it or not
            status = 0
            if os.path.isfile(f'{TORRENT_ROOT}{f_name}.json'):
                # add the torrent to the db
                added = local_db.add_torrent(f'{f_name}.json')
                if added:
                    status = 1
            server.send_msg(ip, ServerProtocol.build_send_added_status(f_name, status))
            # if managed to upload the file, update all the users
            if status == 1:
                server.send_all(ServerProtocol.build_send_file(f_name))


files_q = queue.Queue()
server_by_ip = {}   # dict for all file uploading servers (ip : Server)

# root to the torrents directory
TORRENT_ROOT = 'D:\GTorrent\\'

msg_q = queue.Queue()


# create the database
db = DB("GTorrent")
db_files = db.get_torrents()

if TORRENT_ROOT != '' and not os.path.exists(TORRENT_ROOT):
    os.mkdir(TORRENT_ROOT)

# delete files not in the db
my_files = os.listdir(TORRENT_ROOT)
for file in my_files:
    if file not in db_files:
        # check if it's file or folder to remove
        if '.' in file:
            os.remove(f"{TORRENT_ROOT}{file}")
        else:
            os.rmdir(f"{TORRENT_ROOT}{file}")

server = Server(3000, msg_q)

threading.Thread(target=handle_files, args=(files_q,)).start()

# main loop
while True:
    # receive the message from the server
    ip, data = msg_q.get()
    code = data[:2]
    info = data[2:]

    print(f"RECEIVED FROM {ip} INFO {info}, DATA {data}")

    # send files in the system
    if code == '99'.encode():
        files_in_system = db.get_torrents()
        server.send_msg(ip, ServerProtocol.build_send_file_names(files_in_system))

    # receive files in the client's monitored folder
    elif code == '01'.encode():
        client_files = ServerProtocol.break_recv_file_names(info.decode())
        if '' in client_files:
            client_files.remove('')
        files_in_system = db.get_torrents()
        # check for files not in the system, if there are tell the client to delete them
        for f in client_files:
            if f"{f}.json" not in files_in_system:
                server.send_msg(ip, ServerProtocol.build_delete_file(f))
        # update existing torrent files if the file is deleted from the client
        for f in files_in_system:
            with open(f'{TORRENT_ROOT}\\{f}', 'r') as tFile:
                torrent_data = tFile.read()
            if ip in torrent_data and f[:f.find('.json')] not in client_files:
                torrent_data = torrent_data.replace(ip, '')
                # torrent_data = torrent_data.strip(';')
            if len(torrent_data.split('ip_list')[1]) < len("255.255.255.255"):
                os.remove(f'{TORRENT_ROOT}{f}')
                db.delete_torrent(f'{f}')
                server.send_all(ServerProtocol.build_file_deleted(f[:f.find('.json')]))
            else:
                with open(f'{TORRENT_ROOT}{f}', 'w') as tFile:
                    tFile.write(torrent_data)

    # receive file was deleted from the monitored folder
    elif code == '02'.encode():
        files_in_system = db.get_torrents()
        file_name = ServerProtocol.break_recv_deleted_file(info.decode())
        # update the relevant torrent file with the changes
        if f'{file_name}.json' in files_in_system:
            with open(f"{TORRENT_ROOT}{file_name}.json", 'r') as file:
                torrent = json.load(file)
                if ip in torrent["ip_list"]:
                    torrent["ip_list"] = torrent["ip_list"].replace(ip, '')
                    torrent["ip_list"] = torrent["ip_list"].strip(';')
            # if there are no clients who can share the file, remove it from the system and let the connected users know
            if len(torrent["ip_list"]) > 0 and torrent["ip_list"] != ";":
                with open(f"{TORRENT_ROOT}{file_name}.json", 'w') as file:
                    json.dump(torrent, file)
            else:
                os.remove(f'{TORRENT_ROOT}{file_name}.json')
                db.delete_torrent(f'{file_name}.json')
                server.send_all(ServerProtocol.build_file_deleted(file_name))

    # receive file was added to the monitored folder
    elif code == '03'.encode():
        files_in_system = db.get_torrents()
        file_name = ServerProtocol.break_recv_added_file(info.decode())
        # if the file is not in the system, tell the client to delete it
        if f'{file_name}.json' not in files_in_system:
            server.send_msg(ip, ServerProtocol.build_delete_file(file_name))

    # receive a download was finished
    elif code == '06'.encode():
        files_in_system = db.get_torrents()
        file_name = ServerProtocol.break_recv_finish(info.decode())
        # check if the file is in the system, if so update the relevant torrent file with the changes
        if f'{file_name}.json' in files_in_system:
            with open(f"{TORRENT_ROOT}{file_name}.json", 'r') as file:
                torrent = json.load(file)
                if ip not in torrent["ip_list"]:
                    torrent["ip_list"] += f";{ip}"
            with open(f"{TORRENT_ROOT}{file_name}.json", 'w') as file:
                json.dump(torrent, file)

    # send torrent file
    #TODO: IF THERE IS AN ERROR WITH THE FILE, REMOVE IT FROM THE SYSTEM???
    elif code == '07'.encode():
        tname = ServerProtocol.break_recv_torrent_name(info.decode())
        server.send_msg(ip, ServerProtocol.build_send_torrent(f"{TORRENT_ROOT}{tname}", server.get_ip_list()))

    # create file upload server for the client
    elif code == '20'.encode():
        port = int(info.decode())
        server_by_ip[ip] = Server(port, files_q, 'file_server')
        server.send_msg(ip, ServerProtocol.build_send_port(port))
