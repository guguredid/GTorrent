'''
file for a class representing protocol handler for server
'''
import os
import json


class ServerProtocol:
    '''
    class representing protocol handler for server
    '''

    @staticmethod
    def build_send_file_names(names):
        '''
        return a message for sending system's files names to a client
        :param names: list
        :return: str
        '''
        msg = ';'.join(names)
        return f"01{msg}"

    @staticmethod
    def break_recv_file_names(data):
        '''
        return a list of files from the client's monitored folder
        :param data: str
        :return: list
        '''
        return data.split(';')

    @staticmethod
    def build_delete_file(file_name):
        '''
        return a message for deleting a file in the client's monitored folder
        :param file_name: str
        :return: str
        '''
        return f"02{file_name.ljust(10)}"

    @staticmethod
    def break_recv_deleted_file(data):
        '''
        return the name of the deleted file in the client's monitored folder
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def break_recv_added_file(data):
        '''
        return the name of the new added file in the client's monitored folder
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def break_recv_file(data):
        '''
        return the file name and file data in tuple
        :param data: bytes
        :return: tuple
        '''
        file_name = data[:10].decode().rstrip()
        data = data[10:]
        return file_name, data

    @staticmethod
    def build_file_deleted(file):
        '''
        return a message for deleting a file from the system
        :param file: str
        :return: str
        '''
        return f"09{file.ljust(10)}"

    @staticmethod
    def build_send_added_status(name, status):
        '''
        return a message for updating the client if the file was added to the system or not
        :param name: str
        :param status: int
        :return: str
        '''
        return f"05{name.ljust(10)}{status}"

    @staticmethod
    def break_recv_finish(data):
        '''
        return the name of the file the client finished downloading
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def build_send_file(file_name):
        '''
        return a message for updating a client that a new file was added to the system
        :param file_name: str
        :return: str
        '''
        return f"06{file_name.zfill(6)}"

    @staticmethod
    def break_recv_torrent_name(data):
        '''
        return the wanted torrent name from the message
        :param data: str
        :return: str
        '''
        return data.rstrip()

    @staticmethod
    def build_send_torrent(tname, ip_list):
        '''
        return a message for sending a torrent name to the user
        :param tname: str
        :param ip_list: list
        :return: str
        '''
        data = '!'.encode()
        if os.path.exists(f"{tname}.json"):

            with open(f"{tname}.json", 'r') as file:
                data = json.load(file)
            connected_ips = []
            #
            for ip in ip_list:
                if ip in data["ip_list"]:
                    connected_ips.append(ip)
            print(f"CONNECTED IPS: {connected_ips}")
            # check if there are connected sharing people
            if len(connected_ips) > 0:
                data["ip_list"] = ';'.join(connected_ips)
                print(f"DATA: {data}")

                data = json.dumps(data).encode()
            else:
                data = '!'.encode()

        return "07".encode() + data

    @staticmethod
    def build_send_port(port):
        '''
        return a message for sending a port for a client for his file's server
        :param port: int
        :return: str
        '''
        return f"20{port}"

    @staticmethod
    def build_update_ip(ip, status):
        '''
        return a message for updating a client that a new ip was added\removed to the sharing clients
        :param ip: str
        :param status: 1
        :return: str
        '''
        pass

