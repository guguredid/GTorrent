import ast
'''
file for a class representing torrent file
'''


class Torrent:
    '''
    class representing torrent file
    '''

    def __init__(self, json_str):
        '''
        initializing a torrent object
        :param json_str: str
        '''
        # convert the data from string to dicionary
        t_dict = ast.literal_eval(json_str)

        # data from the torrent file
        self.torrent_name = t_dict["name"].replace('.torrent', '')
        self.num_parts = t_dict["num"]
        self.hash_list = t_dict["hash_list"].split(';')
        self.complete_hash = t_dict["complete_hash"]
        self.ip_list = t_dict["ip_list"].split(';')

    def get_name(self):
        '''
        returns the torrent's name
        :return: str
        '''
        return self.torrent_name

    def get_hash(self):
        '''
        returns the file's hash
        :return: str
        '''
        return self.complete_hash

    def get_parts_hash(self):
        '''
        returns the hashes list
        :return: list
        '''
        return self.hash_list

    def get_ip_list(self):
        '''
        returns the ips list
        :return: list
        '''
        return self.ip_list

    #TODO: DO I NEED THIS FUNCTION???
    def update_ip_list(self, ip, status=0):
        '''
        updates the ip list of the torrent
        :param ip: str
        :param status: int
        :return: None
        '''
        # if the status is 0, delete the given ip
        if status == 0 and ip in self.ip_list:
            self.ip_list.remove(ip)
        # if the status is 1, add the given ip
        else:
            self.ip_list.append(ip)

    #TODO: DO I NEED THIS FUNCTION???
    def to_dict(self):
        '''
        return dict for converting the object to json
        :return: dict
        '''
        return {
            "name": self.torrent_name,
            "num": self.num_parts,
            "hash_list": ";".join(self.hash_list),
            "complete_hash": self.complete_hash,
            "ip_list": ";".join(self.ip_list)
                }
