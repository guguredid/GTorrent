from classes.TorrentHandlerServer import TorrentHandlerServer
from classes.Torrent import Torrent
import json

cat_torrent = TorrentHandlerServer.build_torrent('dog.jpg', "192.168.4.74;192.168.4.73")
# print(cat_torrent["ip_list"])
# cat_torrent["ip_list"] += ";192.168.4.73"
print('CAT TORRENT-', cat_torrent)
with open('dog.jpg.json', 'w') as file:
    file.write(cat_torrent)



# update torrent with new ip
# 192.168.4.73
# new_t = TorrentHandlerServer.update_ip_list('cat.jpg.json', '192.168.4.73', 1)
# with open('cat.jpg.json', 'w') as file:
#     file.write(new_t)

