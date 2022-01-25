from classes.FileHandler import FileHandler
import socket


my_socket = socket.socket()
# available to connect
my_socket.bind(('0.0.0.0', 2000))
# only one client in time
my_socket.listen(1)

# waiting for client
while True:
    client_socket, client_address = my_socket.accept()
    print(f'{client_address[0]} - connected')
    # work until client disconnect
    while True:
        try:
            # get chunk number
            chunk_number = client_socket.recv(4).decode()
        except Exception as e:
            print(f'[ERROR] - in receiving chunk number: {str(e)}')
            break
        else:
            # if empty, disconnect
            if chunk_number == '':
                break
            print(f"ASKED FOR CHUNK {chunk_number}")
            client_socket.send(FileHandler.get_part('cat.jpg', int(chunk_number)))

    # client disconnected - so there being an error
    print(f'{client_address[0]} - disconnected')
    # close the clint and the server - so they will not take a place in the memory
    client_socket.close()
