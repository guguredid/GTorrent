import json
'''
file for a class representing torrent file
'''


class Torrent:
    """
    class representing torrent file
    """

    def __init__(self, json_str):
        """
        initializing a torrent object
        :param json_str: str
        """
        self.ok = False
        # convert the data from string to dictionary
        try:
            t_dict = json.loads(json_str)
        except Exception as e:
            print(f"IN TORRENT! {str(e)}")
        else:
            self.ok = True
            # data from the torrent file
            self.torrent_name = t_dict["name"].replace('.torrent', '')
            self.num_parts = t_dict["num"]
            self.hash_list = t_dict["hash_list"].split(';')
            self.complete_hash = t_dict["complete_hash"]
            self.ip_list = t_dict["ip_list"].split(';')

    def is_ok(self):
        """
        return the flag - managed to turn the json string into Torrent object or not
        :return: bool
        """
        return self.ok

    def get_name(self):
        """
        returns the torrent's name
        :return: str
        """
        return self.torrent_name

    def get_hash(self):
        """
        returns the file's hash
        :return: str
        """
        return self.complete_hash

    def get_parts_hash(self):
        """
        returns the hashes list
        :return: list
        """
        return self.hash_list

    def get_ip_list(self):
        """
        returns the ips list
        :return: list
        """
        return self.ip_list

    #TODO: DO I NEED THIS FUNCTION???
    # def update_ip_list(self, ip, status=0):
    #     '''
    #     updates the ip list of the torrent
    #     :param ip: str
    #     :param status: int
    #     :return: None
    #     '''
    #     # if the status is 0, delete the given ip
    #     if status == 0 and ip in self.ip_list:
    #         self.ip_list.remove(ip)
    #     # if the status is 1, add the given ip
    #     else:
    #         self.ip_list.append(ip)
