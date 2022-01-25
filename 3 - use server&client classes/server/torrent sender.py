from classes.Server import Server
from classes.ServerProtocol import ServerProtocol
import queue


msg_q = queue.Queue()
server = Server(3000, msg_q)

while True:
    # receive the message from the server
    ip, data = msg_q.get().split(';')
    print(f"RECEIVED {data} FROM {ip}")
    code = data[:2]
    info = data[2:]
    if code == '07':
        tname = ServerProtocol.break_recv_torrent_name(info)
        server.send_msg(ip, ServerProtocol.build_send_torrent(tname))
