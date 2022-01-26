from classes.Torrent import Torrent
import json
import hashlib
import os

'''
file for functions building and updating torrent files
'''


class TorrentHandlerServer:
    '''
    class for handling torrent files in the server
    '''

    @staticmethod
    #FINISH
    def build_torrent(file_name, ip):
        '''
        builds a torrent file for the given file, and deletes the file afterward
        :param file_name: str
        :param ip: str
        :return: json
        '''

        # create Torrent object
        tname = f"{file_name}.torrent"
        parts_hash = TorrentHandlerServer._get_parts_hash(file_name)
        whole_hash = TorrentHandlerServer._get_whole_hash(file_name)

        t_dict = {"name": tname,
                  "num": len(parts_hash),
                  "hash_list": ';'.join(parts_hash),
                  "complete_hash": whole_hash,
                  "ip_list": ip
                  }
        t_to_json = json.dumps(t_dict)

        # TODO: DECIDE ON A SPECIFIC ROOT TO BE BEFORE THE FILE NAME (C:/GTorrent/file.txt)
        # delete the temporary file
        os.remove(file_name)

        return t_to_json

    @staticmethod
    def _encrypt(data):
        '''
        get data, return its hash
        :param data: str
        :return: str
        '''
        hasher = hashlib.md5()
        hasher.update(data)
        return hasher.hexdigest()

    @staticmethod
    def _pad_chunk(data):
        '''
        padding the given data to be 1024 bytes
        :param data: bytes
        :return: tuple
        '''
        # flag - did pad the data or not
        not_added = True
        if len(data) < 1024:
            # if the file's length % 1024 = 0 check so we won't add spare spaces to the end of the file
            if len(data) != 0:
                data += (' ' * (1024 - len(data))).encode()
            not_added = False

        return (data, not_added)

    @staticmethod
    def _break_file(path):
        '''
        returns list of the data in the file, splited for chunks of 1024
        :param path: str
        :return: list
        '''
        chunks = []
        read_data = True
        with open(path, 'rb') as file:
            while read_data:
                data, read_data = TorrentHandlerServer._pad_chunk(file.read(1024))
                if len(data) != 0:
                    chunks.append(data)
        return chunks

    @staticmethod
    def _get_whole_hash(file_name):
        '''
        returns the hash for the whole data in the file
        :param file_name: str
        :return: str
        '''
        #TODO: DECIDE ON A SPECIFIC ROOT TO BE BEFORE THE FILE NAME (C:/GTorrent/file.txt)
        with open(file_name, 'rb') as file:
            data = file.read()
        return TorrentHandlerServer._encrypt(data)

    @staticmethod
    def _get_parts_hash(file_name):
        '''
        returns list of hashes for each part of the file
        :return: list
        '''
        # TODO: DECIDE ON A SPECIFIC ROOT TO BE BEFORE THE FILE NAME (C:/GTorrent/file.txt)
        chunks = TorrentHandlerServer._break_file(file_name)
        hash_list = []
        for c in chunks:
            hash_list.append(TorrentHandlerServer._encrypt(c))
        return hash_list

    @staticmethod
    #FINISH
    def update_ip_list(tname, ip, status=0):
        '''
        updates the ip list according to the status, in the given torrent file
        :param tname: str
        :param ip: str
        :param status: int
        :return: json
        '''
        # TODO: DECIDE ON A SPECIFIC ROOT TO BE BEFORE THE FILE NAME (C:/GTorrent/file.txt)
        with open(tname, 'r') as file:
            t_data = json.loads(file.read())
        #TODO: CREATE NEW TORRENT OR CHANGE T_DATA BY THE IP AND STATUS???
        # t = Torrent(t_data['name'], t_data['num'], t_data['hash_list'].split(';'), t_data['complete_hash'], t_data['ip_list'].split(';'))
        # t.update_ip_list(ip, status)
        # # convert back to json and return it
        # t_to_json = json.dumps(t)

        # if the status is 0, delete the given ip
        if status == 0 and ip in t_data['ip_list']:
            t_data['ip_list'].replace(ip, '')
        # if the status is 1, add the given ip
        else:
            t_data['ip_list'] += f';{ip}'
        # return t_to_json
        return t_data
