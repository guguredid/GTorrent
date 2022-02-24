'''
file for a class representing protocol handler for client
'''


class ClientProtocol:
    '''
    class representing protocol handler for client
    '''

    @staticmethod
    def break_files_in_system(data):
        '''
        return a list of files in the system, received from the server
        :param data: str
        :return: list
        '''
        ret = ''
        if len(data) > 0:
            ret = data.split(';')
        return ret

    @staticmethod
    def build_send_file_names(files):
        '''
        return a message for sending the server the files in the monitored folder
        :param files: list
        :return: str
        '''
        files_part = ''
        if len(files) > 0:
            files_part = ';'.join(files)
        return f"01{files_part}"

    @staticmethod
    def break_delete_file(data):
        '''
        return the name of the file to delete from the monitored folder
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def build_send_deleted_file(file_name):
        '''
        return a message for updating the server a file was deleted from the monitored folder
        :param file_name: str
        :return: str
        '''
        return f"02{file_name.ljust(10)}"

    @staticmethod
    def build_add_file(file_name):
        '''
        return a message for updating the server a file was added to the monitored folder
        :param file_name: str
        :return: str
        '''
        return f"03{file_name.ljust(10)}"

    @staticmethod
    def build_add_file_to_system(file_name, data):
        '''
        return a message for the server about adding a new file to the system
        :param file_name: str
        :param data: bytes(???)
        :return: bytes
        '''
        return f"05{file_name.ljust(10)}".encode() + data

    @staticmethod
    def break_added_status(data):
        '''
        return a tuple with data about if a file was added to the system or not
        :param data: str
        :return: tuple
        '''
        return (data[:10].rstrip(), data[10:])

    @staticmethod
    def build_send_finish_download(file_name):
        '''
        return a message for the server about finishing a download
        :param file_name: str
        :return: str
        '''
        return f"06{file_name.ljust(10)}"

    @staticmethod
    def break_recv_new_file(data):
        '''
        return the name of the new file added to the system
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def build_ask_torrent(tname):
        '''
        return a message for asking the server for a torrent file
        :param tname: str
        :return: str
        '''
        return f"07{tname.ljust(10)}"

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
        :return: tuple
        '''
        return data[0], int(data[1:])

    @staticmethod
    def build_ask_part(file_name, part):
        '''
        return a message for asking a part for specific file from a sharer
        :param file_name: str
        :param part: int
        :return: str
        '''
        return f"10{file_name.ljust(10)}{part}"

    @staticmethod
    def break_ask_part(data):
        '''
        return a tuple with the file and the part number
        :param data: bytes
        :return: tuple
        '''
        data = data.decode()
        return data[:10].rstrip(), int(data[10:])

    @staticmethod
    def break_recv_part(data):
        '''
        return a tuple with the file the part is from, the part's number and the part itself
        :param data: bytes
        :return: tuple
        '''
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
    def break_recv_port(data):
        '''
        return the port sent for client
        :param data: bytes
        :return: int
        '''
        return data[2:].decode()

    @staticmethod
    def build_disconnect():
        '''
        return a message for disconnecting from a sharer
        :return: str
        '''
        return "12"
