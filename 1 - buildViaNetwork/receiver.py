from classes.FileHandler import FileHandler
import socket
import threading


def handle_share(ip, id):
    '''
    handles the connection with one sharing user
    :param soc: Socket
    :return: None
    '''
    global file_event, chunks_to_write, chunks_busy
    soc = socket.socket()
    try:
        soc.connect((ip, 2000))
    except Exception as e:
        print(f"ERROE! {str(e)}")
    else:

        print(f"THREAD {id} STARTED!")
        while len(chunks_to_write) > 0 or len(chunks_busy) > 0:
            if len(chunks_to_write) > 0:
                current_chunk = chunks_to_write.pop(0)
                # chunks_to_write.remove(current_chunk)
                chunks_busy.append(current_chunk)

            print(f"{id} - CURRENT WORKING ON CHUNK {current_chunk}")
            # connect to the client - SHOULD BE HERE OR IN THE MAIN LOOP???
            try:
                #TODO: SET TIMEOUT WITH soc.settimeout(...)???
                soc.send(f"{current_chunk}".zfill(2).encode())
                chunk = soc.recv(1024)
            except Exception as e:
                print(f"[ERROR] in handle_share - {str(e)} id={id}")
                break
            else:
                # wait until can update the file
                file_event.wait()
                # lock the thread to prevent other threads from using it
                file_event.clear()
                # insert the chunk to the file
                FileHandler.insert_part('copy_cat.jpg', chunk, current_chunk)
                # unlock the event for next thread
                file_event.set()
                if current_chunk in chunks_busy:
                    chunks_busy.remove(current_chunk)


# number of chunks to ask
chunks_num = 45
# list of the chunks still needed
chunks_to_write = [i for i in range(1, 46)]
# list of the chunks being taken care of
chunks_busy = []
# event object
file_event = threading.Event()
file_event.set()
# computers to download from
#CHANGE THE IP!!
ip_list = ["192.168.4.98", "192.168.4.74", "192.168.4.73"]

# create a socket
soc1 = socket.socket()
soc2 = socket.socket()
soc3 = socket.socket()

try:
    soc1.connect((ip_list[0], 2000))
    soc2.connect((ip_list[1], 2000))
    soc3.connect((ip_list[2], 2000))
except Exception as e:
    print('[ERROR] in connecting to senders')
else:
    threading.Thread(target=handle_share, args=(ip_list[0], 1,)).start()
    # # time.sleep(0.5)
    threading.Thread(target=handle_share, args=(ip_list[1], 2,)).start()
    # # time.sleep(0.5)
    threading.Thread(target=handle_share, args=(ip_list[2], 3,)).start()

soc1.close()
soc2.close()
soc3.close()

print('TESTING GIT!')
