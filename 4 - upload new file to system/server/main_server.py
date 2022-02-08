from classes.DB import DB
from classes.Server import Server
from classes.ServerProtocol import ServerProtocol
from classes.TorrentHandlerServer import TorrentHandlerServer
import queue
import os
import threading


def handle_files(q):
    '''
    handles the queue for uploading files to the system.
    :param q: Queue
    :return: None
    '''
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
            if os.path.isfile(f'{TORRENT_ROOT}{f_name}.json'):
                # add the torrent to the db
                added = local_db.add_torrent(f'{f_name}.json')
                if added:
                    print("SENDING OK")
                    server_by_ip[ip].send_msg(ip, ServerProtocol.build_send_added_status(f_name, 1))
                else:
                    print("SENDING NOT OK")
                    server_by_ip[ip].send_msg(ip, ServerProtocol.build_send_added_status(f_name, 0))
            else:
                print("SENDING NOT OK")
                server_by_ip[ip].send_msg(ip, ServerProtocol.build_send_added_status(f_name, 0))


files_q = queue.Queue()
server_by_ip = {}   # dict for all file uploading servers (ip : Server)

# root to the torrents directory
TORRENT_ROOT = 'C:\GTorrent\\'
# TORRENT_ROOT = ''

msg_q = queue.Queue()
server = Server(3000, msg_q)

threading.Thread(target=handle_files, args=(files_q, )).start()

# create the database
db = DB("GTorrent")
# db.delete_torrent('')

print(f"FILES IN DB: {db.get_torrents()}")

#TODO: CREATE C:\GTorrent IF DOES NOT EXIST
if TORRENT_ROOT != '' and not os.path.exists(TORRENT_ROOT):
    os.mkdir(TORRENT_ROOT)

# main loop
while True:
    # receive the message from the server
    ip, data = msg_q.get()
    # # print(f"RECEIVED {data} FROM {ip}")
    code = data[:2]
    info = data[2:]

    print(f"RECEIVED FROM {ip} DATA {info}")

    # send files in the system
    if code == '01'.encode():
        files_in_system = db.get_torrents()
        server.send_msg(ip, ServerProtocol.build_send_file_names(files_in_system))

    # send torrent file
    elif code == '07'.encode():

        tname = ServerProtocol.break_recv_torrent_name(info.decode())
        print(f"SENDING TORRENT FOR {tname}")
        msg = ServerProtocol.build_send_torrent(f"{TORRENT_ROOT}{tname}")
        print(f"MESSAGE!!! {msg}")
        server.send_msg(ip, ServerProtocol.build_send_torrent(f"{TORRENT_ROOT}{tname}"))

    # create file upload server
    elif code == '20'.encode():
        port = int(info.decode())
        print(f"SENDING {ip} PORT {port}")
        server_by_ip[ip] = Server(port, files_q, 'file_server')
        server.send_msg(ip, str(port))
