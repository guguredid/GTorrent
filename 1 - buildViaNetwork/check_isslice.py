from classes.FileHandler import FileHandler
import random


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


def break_file(path):
    '''
    returns list of the data in the file, splited for chunks of 1024
    :param path: str
    :return: list
    '''
    chunks = []
    read_data = True
    with open(path, 'rb') as file:
        while read_data:
            data, read_data = _pad_chunk(file.read(1024))
            chunks.append(data)
    return chunks

'''
using isslice(file, start, end) on file gives the lines in the file from start to end (line1 = index 0, lastline = end-1)
'''
# with open('cat.jpg', 'rb') as file:
#     print(list(itertools.islice(file, 1)))

# for i in itertools.islice(range(20), 1, 5):
#     print(i)

# with open('test.txt', 'wb') as file:
#     file.write(('0'*1026).encode())
# #
# # ret = break_file('test.txt')
# # ret = break_file('cat.jpg')
# # print(len(ret), ret[-1], len(ret[-1]))
# # print(f"FIRST CHUNK={len(ret[0])}, 0={ret[0].count('0'.encode())}, SECOND CHUNK={len(ret[1])}, 0={ret[1].count('0'.encode())}")
#
# chunk2 = FileHandler.get_part('test.txt', 2)
# print(chunk2, len(chunk2), chunk2.count(' '.encode()))

#TODO: SOLUTION FOR SHORT FILES
# mystring = 'some string'
# pos = 10
#
# with open('/path/to/file.txt', 'r+') as f:
#     contents = f.read()
#     contents = contents[:pos] + mystring + contents[pos + 1:]
#     f.seek(0)
#     f.truncate()
#     f.write(contents)
#USE REPLACE???

'testwriteoffile.txt'

FileHandler.insert_part('testwriteoffile.txt', '     '.encode(), 1)
FileHandler.insert_part('testwriteoffile.txt', 'xxxx'.encode(), 2)


# check the cat file!
cat_chunks = break_file('cat.jpg')
print(len(cat_chunks))
numbers = [i for i in range(len(cat_chunks))]
numbers_without = numbers.copy()
random.shuffle(numbers)

for num in numbers:
    FileHandler.insert_part('copy_cat.jpg', cat_chunks[num], num+1)

# copy the image
# for i in range(len(cat_chunks)):
#     FileHandler.insert_part('copy_cat.jpg', cat_chunks[i], i+1)

numbers_without.remove(37)
# print(numbers_without)
for num in numbers_without:
    FileHandler.insert_part('copy_cat2.jpg', cat_chunks[num], num+1)
FileHandler.insert_part('copy_cat2.jpg', FileHandler.get_part('cat.jpg', 38), 38)

