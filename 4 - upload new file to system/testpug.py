from classes.TorrentHandlerServer import TorrentHandlerServer

# hash_list = 'e872ef511abf1abe2a71e653b33c06fc;4376c121cb1982e604845936f04e78d5;8d1a7c3df1aa351ac2f16ebc19ff88f3;6d07081d8ce4b4e8b3340aafdf974d73;e600f8af82f1e22152badcbd79c299b2;75b4fed90fe51bd4f17c853b67af82f3;21eac9c8445f7181354daf4c2e13fa1f;82044f051cd16ecd94f9faab135cdcdb;dd7c4f0137e7c8d1820c5af921446e36;bf56323fb4eac5b5cd1c22cc15a2c908;0f52b7201edc351fc5820280cbccd3c5;057d280ded98f9ff33c3d91336b8916c;5173bf25acf55320ca33d8577881066f;c6409c96372cba69fe8b3d9c3a34a3aa;f06c41c4261320b87f617391b89dcf2d;f199c065cbbbe07269e85fca0535e377;651223ce416b1f4de60dd384b2d20cf5;acf1bc7782d23d3994883a73eb14fe11;e7d3c48e7b9387614d124fb9664e00db;0cdb6f8f67ed0c73077d5b47aa3ffffd;bcf7bf28d6fa00c07f3f80fe4573b1a4;d72bfbc57fc7296759088521c3eb3c78;de93d2c96ee3c57c0c21e14f6d9b7529;c2225c5e586627c0943400b1175d1726;3b7689ed2340fd1eaf3aed8d74594800;045929e7851c47061ed61267aee2e2ad;bcea415195d71ceb143d1db2c09c6c83;08f1e5c5064870ab5e9fa8c73d1b22fe;8ee36ed5abf063aaf9bb36fea5338743'.split(';')
#
# torrent_hash = TorrentHandlerServer._get_parts_hash('pug.jpg')
# print(torrent_hash)
# for i in range(0, len(hash_list)):
#     print(hash_list[i] == torrent_hash[i])

#29,543
# print('LEFT IN THE END:', 29543%1024, f' , NEED TO ADD {1024-(29543%1024)} SPACES!')
# print(29543//1024)
#
# with open('cat.jpg', 'rb') as f:
#     data = f.read()
#     print(len(data))
#     print(len(data.rstrip()))

import win32con
import win32file
import threading

def monitor_dir():
    '''
    monitors changes in the files directory, and reports them
    :return: None
    '''
    hDir = win32file.CreateFile(
        FILES_ROOT,
        win32con.FILE_SHARE_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    # monitor the directory
    while True:

        msg = ''

        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY |
            # NEW
            win32con.FILE_NOTIFY_CHANGE_SIZE,
            None,
            None
        )

        #TODO: SEND THE SERVER WHEN FINISH DOWNLOADING A FILE BY CLOSING IT???

        print(f"RESULT - {results}")

        # 1 : created file
        if results[0][0] == 1:
            print(f' - Created file - {results[0][1]}')

        # 2 : deleted file
        elif results[0][0] == 2:
            print(f' - Deleted file - {results[0][1]}')

        elif results[0][0] == 3:
            print(f' - resize file - {results[0][1]}')

FILES_ROOT = "C:\\Test"
threading.Thread(target=monitor_dir).start()
