from classes.Server import Server
from classes.ServerProtocol import ServerProtocol
from classes.TorrentHandlerServer import TorrentHandlerServer
import queue
import os


msg_q = queue.Queue()
server = Server(3000, msg_q)

while True:
    # receive the message from the server
    # ip, data = msg_q.get().split(';')
    ip, data = msg_q.get()
    # print(f"RECEIVED {data} FROM {ip}")
    code = data[:2]
    info = data[2:]

    # receive new file to the system
    if code == '05'.encode():
        # receive new file
        f_name, data = ServerProtocol.break_recv_file(info)

        print(f"RECEIVED FILE {f_name} AND THE DATA {len(data)}")

        # save temporarily and create json file to it

        with open(f"temp{f_name}", 'wb') as f:
            f.write(data)
        temp_torrent = TorrentHandlerServer.build_torrent(f"temp{f_name}", ip)
        with open(f'{f_name}.json', 'w') as file:
            file.write(temp_torrent)

        # update if managed to do it or not
        if os.path.isfile(f'{f_name}.json'):
            server.send_msg(ip, ServerProtocol.build_send_added_status(f_name, 1))
        else:
            server.send_msg(ip, ServerProtocol.build_send_added_status(f_name, 0))

    # send torrent file
    elif code == '07'.encode():
        tname = ServerProtocol.break_recv_torrent_name(info.decode())
        server.send_msg(ip, ServerProtocol.build_send_torrent(tname))

