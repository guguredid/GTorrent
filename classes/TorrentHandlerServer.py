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

        #{"name": "cat.jpg.torrent", "num": 45, "hash_list": "1ec0cd431a1f3a9149a362c0500d1e1a;a02a2bd23b7bbd9f1fe81603aa2ba71e;480839479780f2b650780b8bdd968044;a598d6269e3b5c27d8386106250484d6;9b3d034e6d01a843b547db7f24ba0a2a;2eca2ab2458004276907d9d497311bc8;fed557177e971ae0f15e138a8ddeec9f;5757944f387f5898887998ec87b505ce;71c5bf35b250204706663c2f37d653f8;5986d4542768f992a97ca81069aeb836;f0493a139d966c4e0909e9d9c136e0c8;4369c6aabff8c661e74bb7a41d7e9b20;c420786b040a67a62a31b573a3d4b9a4;de0dd4405616001fffb94f6b16be5914;5fe06847793c6e119c0502a56903f5b0;8126cbd56c5072441a0985f117305efa;8b3ce5b6cf8f4a68b460a72f23dba591;4de86f4b54b215f6d1e6a1023eeead3c;cb74b2f234b02748125fce809da6f9d4;2c4680be8d5eef996965d72598ccb0ad;b180327fecce71a169836b5a607206b3;7685a9cfb3264ae0354a052ebaf63d43;f1787840ac6b25e997216903ccf6f44d;8d01e523dabf5d354b677ed1ad7ce836;52a92922aa3c786d6ddb74062d50a81b;a85b7b54728067e743dfb5aec3d3cc31;6cee3cd6a58f0cc9e9159ae1396b0a97;5afa8318f5af4616003523b876dc2517;2178574d31b79245aec81012d215201e;2ada2d26e6d9843822e35071fc3cb0d6;54bb704d0cf25844606e9e84e2884eb8;def628da3ece3e240c56b2d9cddb65d0;cd980e6e33ea6aaffb4698e333754779;47e9d429ed986fce0febb4cced4c4efb;a7bd161891adf5bc9bdfea817c26a2de;ab1de34e869e6f7bd94fb905279164f0;665713d7bfebbb8edb2ba03cd1c84786;ad51caef2de9f6d39c31d43a14b1d822;10c1c686338821b7f84a36a5bee4ba98;c07fc54b154ce9f0b788aa2485f1495d;0f191ccee747e7ad87d4d3b2f0ba2575;22169c26a6b27d514c78c801e01f0cf7;3ea2502c58296f3678d2e58252569583;772e1341619543c0f413ba947e0da9c5;d44df325d4703f9b88fbb35830820e45", "complete_hash": "002e09169dc037f86f93561d6049404d", "ip_list": "127.0.0.1"}

        # create Torrent object
        tname = f"{file_name}.torrent"
        parts_hash = TorrentHandlerServer._get_parts_hash(file_name)
        whole_hash = TorrentHandlerServer._get_whole_hash(file_name)
        print(f"PROT2 {len(whole_hash)}")

        t_dict = {"name": tname,
                  "num": len(parts_hash),
                  "hash_list": ';'.join(parts_hash),
                  "complete_hash": whole_hash,
                  "ip_list": ip
                  }
        t_to_json = json.dumps(t_dict)

        # t = Torrent(tname, len(parts_hash), parts_hash, whole_hash, [ip])
        # # turn the torrent to json
        # t_to_json = json.dumps(t.to_dict())
        # # save the json file
        # with open(tname, 'w') as file:
        #     file.write(t_to_json)

        # TODO: DECIDE ON A SPECIFIC ROOT TO BE BEFORE THE FILE NAME (C:/GTorrent/file.txt)
        # delete the temporary file
        os.remove(file_name)
        # return the json object
        # print('IN CLASS ', t_to_json, type(t_to_json))
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
        print(f"IN PROTOCOL {len(data)}")
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
