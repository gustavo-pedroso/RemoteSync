import _thread
import math
import os
import util
import constants as const
import socket
from queue import Queue


class ClientSynchronizer:

    def __init__(self, server_address, server_port, folder, n_threads):
        self.server_address = server_address
        self.server_port = server_port
        self.threadPool = Queue(maxsize=n_threads)
        i = 0
        while not self.threadPool.full():
            self.threadPool.put(i)
            i += 1

        self.meta_data = {}
        for file in folder:
            if not os.path.isdir(file):
                self.meta_data[file] = create_chunk_hash_map(file)
            else:
                self.meta_data[file] = None

    def find_changes(self, files):

        modifications = []
        deleted = []
        created = []
        updated = []

        for file in self.meta_data.keys():  # check if any file was deleted
            if file not in files:
                modifications.append(('delete', 0, file, None))
                deleted.append(file)

        for file in files:  # check if any file was created
            if file not in self.meta_data.keys():
                if not os.path.isdir(file):
                    modifications.append(('create', get_size_in_chunks(file), file, self.get_modifications(file)))
                    created.append(file)
                    self.meta_data[file] = create_chunk_hash_map(file)
                else:
                    modifications.append(('create', 0, file, None))
                    self.meta_data[file] = {}

        for file in files:  # check if any file was updated
            if file in self.meta_data.keys():
                if not os.path.isdir(file):
                    if create_chunk_hash_map(file) != self.meta_data[file]:
                        modifications.append(('update', get_size_in_chunks(file), file, self.get_modifications(file)))
                        updated.append(file)

        for f in deleted:
            del self.meta_data[f]
        for f in created:
            self.meta_data[f] = create_chunk_hash_map(f)
        for f in updated:
            self.meta_data[f] = create_chunk_hash_map(f)

        for m in modifications:
            while self.threadPool.empty():
                continue
            worker = self.threadPool.get()
            _thread.start_new_thread(self.transfer, (worker, m, ))

    def get_modifications(self, file):
        actual_data = create_chunk_map(file)
        actual_data_hash = create_chunk_hash_map(file)
        modifications = {}

        if file in self.meta_data:
            for a in actual_data_hash.keys():
                if a in self.meta_data[file]:
                    if self.meta_data[file][a] != actual_data_hash[a]:
                        modifications[a] = actual_data[a]
                else:
                    modifications[a] = actual_data[a]
        else:
            modifications = actual_data

        return modifications

    def transfer(self, worker, mod):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_address, self.server_port))
        payload = util.serialize(mod)
        s.sendall(payload)
        s.close()
        self.threadPool.put(worker)


def get_size_in_chunks(file):
    file_size = os.stat(file).st_size - 1
    size_in_chunks = int(math.ceil(file_size/const.chunk_size))
    return size_in_chunks


def create_chunk_hash_map(file):
    size_in_chunks = get_size_in_chunks(file)
    chunk_hash_map = {}
    fd = open(file, 'rb')
    for i in range(0, size_in_chunks):
        chunk_hash_map[i] = hash(fd.read(const.chunk_size))
    return chunk_hash_map


def create_chunk_map(file):
    size_in_chunks = get_size_in_chunks(file)
    chunk_map = {}
    fd = open(file, 'rb')
    for i in range(0, size_in_chunks):
        chunk_map[i] = fd.read(const.chunk_size)
    return chunk_map



