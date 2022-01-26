from classes.TorrentHandlerServer import TorrentHandlerServer
from classes.Torrent import Torrent
import json



#{"name": "cat.jpg.torrent", "num": 45, "hash_list": "1ec0cd431a1f3a9149a362c0500d1e1a;a02a2bd23b7bbd9f1fe81603aa2ba71e;480839479780f2b650780b8bdd968044;a598d6269e3b5c27d8386106250484d6;9b3d034e6d01a843b547db7f24ba0a2a;2eca2ab2458004276907d9d497311bc8;fed557177e971ae0f15e138a8ddeec9f;5757944f387f5898887998ec87b505ce;71c5bf35b250204706663c2f37d653f8;5986d4542768f992a97ca81069aeb836;f0493a139d966c4e0909e9d9c136e0c8;4369c6aabff8c661e74bb7a41d7e9b20;c420786b040a67a62a31b573a3d4b9a4;de0dd4405616001fffb94f6b16be5914;5fe06847793c6e119c0502a56903f5b0;8126cbd56c5072441a0985f117305efa;8b3ce5b6cf8f4a68b460a72f23dba591;4de86f4b54b215f6d1e6a1023eeead3c;cb74b2f234b02748125fce809da6f9d4;2c4680be8d5eef996965d72598ccb0ad;b180327fecce71a169836b5a607206b3;7685a9cfb3264ae0354a052ebaf63d43;f1787840ac6b25e997216903ccf6f44d;8d01e523dabf5d354b677ed1ad7ce836;52a92922aa3c786d6ddb74062d50a81b;a85b7b54728067e743dfb5aec3d3cc31;6cee3cd6a58f0cc9e9159ae1396b0a97;5afa8318f5af4616003523b876dc2517;2178574d31b79245aec81012d215201e;2ada2d26e6d9843822e35071fc3cb0d6;54bb704d0cf25844606e9e84e2884eb8;def628da3ece3e240c56b2d9cddb65d0;cd980e6e33ea6aaffb4698e333754779;47e9d429ed986fce0febb4cced4c4efb;a7bd161891adf5bc9bdfea817c26a2de;ab1de34e869e6f7bd94fb905279164f0;665713d7bfebbb8edb2ba03cd1c84786;ad51caef2de9f6d39c31d43a14b1d822;10c1c686338821b7f84a36a5bee4ba98;c07fc54b154ce9f0b788aa2485f1495d;0f191ccee747e7ad87d4d3b2f0ba2575;22169c26a6b27d514c78c801e01f0cf7;3ea2502c58296f3678d2e58252569583;772e1341619543c0f413ba947e0da9c5;d44df325d4703f9b88fbb35830820e45", "complete_hash": "002e09169dc037f86f93561d6049404d", "ip_list": "127.0.0.1"}

cat_torrent = TorrentHandlerServer.build_torrent('dog.jpg', "127.0.0.1;192.168.4.74")
# cat_torrent = TorrentHandlerServer.build_torrent('cat.jpg', "127.0.0.1")
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

