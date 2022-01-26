'''
file for a class representing protocol handler for client
'''


class ClientProtocol:
    '''
    class representing protocol handler for client
    '''

    @staticmethod
    def break_file_in_system(data):
        '''
        return a list of files in the system, recevied from the server
        :param data: str
        :return: list
        '''
        pass

    @staticmethod
    def build_send_file_names(files):
        '''
        return a message for sending the server the files in the monitored folder
        :param files: list
        :return: str
        '''
        pass

    @staticmethod
    def break_delete_file(data):
        '''
        return the name of the file to delete from the monitored folder
        :param data: str
        :return: str
        '''
        pass

    @staticmethod
    def build_send_deleted_file(file_name):
        '''
        return a message for updating the server a file was deleted from the monitored folder
        :param file_name: str
        :return: str
        '''
        pass

    @staticmethod
    def build_add_file(file_name):
        '''
        return a message for updating the server a file was added to the monitored folder
        :param file_name: str
        :return: str
        '''
        pass

    #TODO: DO I SPLIT THE MESSAGE OR WHAT
    @staticmethod
    def build_add_file_to_system(file_name, data):
        '''
        return a message for the server about adding a new file to the system
        :param file_name: str
        :param data: bytes(???)
        :return: bytes
        '''
        # return f"05{file_name.ljust(10)}{str(len(data)).zfill(6)}".encode() + data
        return f"05{file_name.ljust(10)}".encode() + data
        # pass

    @staticmethod
    def break_added_status(data):
        '''
        return a tuple with data about if a file was added to the system or not
        :param data: str
        :return: tuple
        '''
        return (data[:10].rstrip(), data[10:])
        # pass

    @staticmethod
    def break_recv_new_file(data):
        '''
        return the name of the new file added to the system
        :param data: str
        :return: str
        '''
        pass

    @staticmethod
    def build_ask_torrent(tname):
        '''
        return a message for asking the server for a torrent file
        :param tname: str
        :return: str
        '''
        # code 07
        return f"07{tname.ljust(10)}"
        pass

    @staticmethod
    def break_recv_torrent(data):
        '''
        return a Torrent object from the data(?????)
        :param data: str
        :return: Torrent(???)
        :return: str
        '''

        pass

    @staticmethod
    def break_update_ip(data):
        '''
        return a tuple with data about the ip and its status (added\removed)
        :param data: str
        :return: str
        '''
        pass

    @staticmethod
    def build_ask_part(file_name, part):
        '''
        return a message for asking a part for specific file from a sharer
        :param file_name: str
        :param part: int
        :return: str
        '''
        # return f"10{file_name.ljust(10)}{str(part).zfill(4)}part"
        return f"10{file_name.ljust(10)}{part}"
        # pass

    @staticmethod
    def break_ask_part(data):
        '''
        return a tuple with the file and the part number
        :param data: bytes
        :return: tuple
        '''
        # return (data[2:12].decode(), int(data[12:16]), data[16:])
        data = data.decode()
        return data[:10], int(data[10:])
        # pass

    @staticmethod
    def break_recv_part(data):
        '''
        return a tuple with the file the part is from, the part's number and the part itself
        :param data: bytes
        :return: tuple
        '''
        # file_name = data[2:12].decode().rstrip()
        # current_chunk = int(data[12:16]).decode()
        # chunk = data[16:]
        # return (file_name, current_chunk, chunk)
        return (data[2:12].decode().rstrip(), int(data[12:16]), data[16:])

    @staticmethod
    def build_send_part(file_name, num, data):
        '''
        return a message for sending a file's part to someone
        :param file_name: str
        :param num: int
        :param data: bytes(????)
        :return: str\bytes????
        '''
        return f"11{file_name.ljust(10)}{str(num).zfill(4)}".encode() + data

    @staticmethod
    def build_disconnect():
        '''
        return a message for disconnecting from a sharer
        :return: str
        '''
        pass









