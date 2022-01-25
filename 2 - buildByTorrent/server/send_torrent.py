from classes.TorrentHandlerServer import TorrentHandlerServer
import socket
import os

my_socket = socket.socket()
# available to connect
my_socket.bind(('0.0.0.0', 3000))
# only one client in time
my_socket.listen(1)

while True:
    client_socket, client_address = my_socket.accept()
    print(f'{client_address[0]} - connected')
    # work until client disconnect
    while True:
        try:
            # get the torrent name
            tname = client_socket.recv(10).decode().rstrip()
        except Exception as e:
            print(f'[ERROR] - in receiving chunk number: {str(e)}')
            break
        else:
            # if empty, disconnect
            if tname == '':
                break
            print(f"THE ASKED FILE - {tname}.json")
            # check if the file exist
            if os.path.isfile(f"{tname}.json"):

                with open(f"{tname}.json", 'rb') as file:
                    tdata = file.read()
            try:
                client_socket.send(str(len(tdata)).zfill(5).encode())
                client_socket.send(tdata)
            except Exception as e:
                print(f'[ERROR] in sending torrent - {str(e)}')

    # client disconnected - so there being an error
    print(f'{client_address[0]} - disconnected')
    # close the clint and the server - so they will not take a place in the memory
    client_socket.close()



