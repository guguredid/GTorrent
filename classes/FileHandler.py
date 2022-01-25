import os
'''
file for functions for breaking and building files
'''


class FileHandler:
    '''
    class for building and breaking files
    '''

    #TODO: WHY NEED THE STATIC IS PRIVATE FUNCTION!!
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
    def get_part(path, num):
        '''
        return specific chunk from a given file
        :param path: str
        :param num: int
        :return: bytes
        '''
        with open(path, 'rb') as file:
            file.seek(((num - 1) * 1024))
            chunk = FileHandler._pad_chunk(file.read(1024))[0]
        return chunk

    @staticmethod
    def insert_part(path, data, num):
        '''
        insert the given data in the given file in the specific place
        :param path: str
        :param data: bytes
        :param num: int
        :return: None
        '''
        # check if the file exist first
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                pass
        # write the data to the file after checking he's existing
        with open(path, 'r+b') as file:
            file.seek(((num - 1) * 1024))
            file.write(data)
