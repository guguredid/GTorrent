import win32file
import win32con
import os

# directory = input('Enter the directory you want to follow: ')
DIRECTORY = 'C:\GTorrent'

# loop while the directory is not correct
while not os.path.isdir(DIRECTORY):
    directory = input('Enter the directory you want to follow: ')

hDir = win32file.CreateFile (
  DIRECTORY,
  win32con.FILE_SHARE_READ,
  win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
  None,
  win32con.OPEN_EXISTING,
  win32con.FILE_FLAG_BACKUP_SEMANTICS,
  None
)

# configure the logger settings - what file to write to and in what format (message only)
# logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='w', format='%(message)s')

# monitor the directory
while True:

    new_log = ''

    results = win32file.ReadDirectoryChangesW(
        hDir,
        1024,
        True,
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
        win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
        win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
        win32con.FILE_NOTIFY_CHANGE_SIZE |
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
        win32con.FILE_NOTIFY_CHANGE_SECURITY,
        None,
        None
    )

    # 1 : created file
    if results[0][0] == 1:
        # new_log = f'{datetime.datetime.now()} - Created file - {results[0][1]}\n'
        new_log = f'Created file - {results[0][1]}\n'
    # 2 : deleted file
    elif results[0][0] == 2:
        # new_log = f'{datetime.datetime.now()} - Deleted file - {results[0][1]}\n'
        new_log = f'Deleted file - {results[0][1]}\n'
    # # 3 : updated file
    # elif results[0][0] == 3:
    #     new_log = f'{datetime.datetime.now()} - Updated file - {results[0][1]}\n'
    # # 4 : renamed
    # elif results[0][0] == 4:
    #     new_log = f'{datetime.datetime.now()} - Renamed file - from {results[0][1]} to {results[1][1]}\n'

    # print the LOG
    print(new_log, end='')


