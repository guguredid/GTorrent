import sqlite3


class DB:
    '''
    class that handles the work between the server and the data base
    '''

    def __init__(self, name):
        '''
        create data base with the given name
        :param name: str
        '''
        self.db_name = name
        # data base variables
        self.tbl_name = 'TorrentData'   # table name
        self.con = None
        self.cursor = None

        self._createDB()

    def _createDB(self):
        '''
        create / connect data base
        :return: None
        '''
        # create / connect data base
        self.con = sqlite3.connect(self.db_name)
        self.cursor = self.con.cursor()

        # create table in the data base
        cmd = f'CREATE TABLE IF NOT EXISTS {self.tbl_name} (name TEXT)'
        self.cursor.execute(cmd)

        # make the changes right now
        self.con.commit()

    def _name_exist(self, name):
        '''
        checks if the given name appears in the db
        :param name: str
        :return: bool
        '''
        cmd = f"SELECT name FROM {self.tbl_name} WHERE name='{name}'"
        self.cursor.execute(cmd)
        return len(self.cursor.fetchall()) != 0

    def add_torrent(self, name):
        '''
        adds new torrent file
        :param name: str
        :return: bool
        '''
        # flag - managed to add the torrent
        flag = False
        if not self._name_exist(name):
            cmd = f"INSERT INTO {self.tbl_name} VALUES ('{name}') "
            self.cursor.execute(cmd)
            self.con.commit()
            flag = True
        return flag

    def delete_torrent(self, name):
        '''
        delete torrent from the db, return true if managed to do it
        :param name: str
        :return: bool
        '''
        # flag - managed to delete the torrent or not
        flag = False
        if self._name_exist(name):
            cmd = f"DELETE FROM {self.tbl_name} WHERE name='{name}'"
            self.cursor.execute(cmd)
            self.con.commit()
            flag = True
        return flag

    def get_torrents(self):
        '''
        returns a list of the torrent files in the system
        :return: list
        '''
        cmd = f"SELECT name FROM {self.tbl_name} WHERE {1==1}"
        self.cursor.execute(cmd)
        data = self.cursor.fetchall()
        names_list = []
        for tup in data:
            names_list.append(tup[0])
        return names_list

    def close_db(self):
        '''
        close connection to the db
        :return: None
        '''
        self.con.close()
