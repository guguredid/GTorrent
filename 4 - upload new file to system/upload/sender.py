from classes.FileHandler import FileHandler
from classes.Server import Server
from classes.ClientProtocol import ClientProtocol
import queue


msg_q = queue.Queue()
server = Server(2000, msg_q)

while True:
    # receive the message from the server
    ip, data = msg_q.get().split(';')
    print(f"RECEIVED {data} FROM {ip}")
    code = data[:2]
    info = data[2:]
    if code == '10':
        file_name, part = ClientProtocol.break_ask_part(info)
        file_name = file_name.rstrip()
        print(f"THE WANTED FILE - {file_name}, ASKED FOR CHUNK {part}")
        # CHECK THE FILE LENGTH
        # with open(file_name, 'rb') as file:
        #     data = file.read()
        #     print(f"DATA LEN - {len(data)}")
        server.send_part(ip, ClientProtocol.build_send_part(file_name, part, FileHandler.get_part(file_name, part)))
