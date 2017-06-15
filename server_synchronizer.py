import util
import constants as const
import _thread
import os
import threading
import socket

threadLock = threading.Lock()


class ServerSynchronizer:

    def __init__(self, port):
        self.port = port
        self.user_home = os.getcwd()+'/USER_AT_'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket.gethostname(), self.port))

    def get_connections(self):
        self.sock.listen()
        while True:
            cs, ca = self.sock.accept()
            user_folder = self.user_home+str(ca[0])
            _thread.start_new_thread(sync_handler, (cs, user_folder,))


def sync_handler(cs, user_folder):
    response = b''.join(recvall(cs))
    cs.close()
    payload = util.deserialize(response)

    mode = payload[0]
    size_in_chunks = payload[1]
    file = payload[2]
    mod_map = payload[3]

    local_folder, local_file = util.split_path(user_folder, file)
    local_file_path = local_folder + '/' + local_file

    if mode == 'create':
        create(file, local_file_path, local_folder, size_in_chunks, mod_map)
    elif mode == 'delete':
        delete(file, local_file_path)
    elif mode == 'update':
        update(file, local_file_path, local_folder, local_file, size_in_chunks, mod_map)


def create(file, local_file_path, local_folder, size_in_chunks, mod_map):
    print('synchronizing ', file, '...')
    threadLock.acquire()
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    threadLock.release()
    if mod_map is not None:
        fd = open(local_file_path, 'wb')

        for i in range(0, size_in_chunks):
            if i in mod_map:
                fd.write(mod_map[i])

        fd.close()
    else:
        os.mkdir(local_file_path)
    return


def delete(file, local_file_path):
        if const.delete_flag:
            print('deleting ', file, '...')
            if not os.path.isdir(local_file_path):
                try:
                    os.remove(local_file_path)
                except IOError:
                    pass
            else:
                try:
                    os.rmdir(local_file_path)
                except IOError:
                    pass
        return


def update(file, local_file_path, local_folder, local_file, size_in_chunks, mod_map):
    print('synchronizing ', file, '...')
    fd = open(local_file_path, 'rb')
    fd1 = open(local_folder + '/temp_' + local_file, 'wb')

    for i in range(0, size_in_chunks):
        chunk = fd.read(const.chunk_size)
        if i in mod_map:
            fd1.write(mod_map[i])
        else:
            fd1.write(chunk)

    os.remove(local_file_path)
    os.rename(local_folder + '/temp_' + local_file, local_file_path)
    fd.close()
    fd1.close()
    return


def recvall(sock, buffer_size=const.msg_len):
    buf = sock.recv(buffer_size)
    while buf:
        yield buf
        buf = sock.recv(buffer_size)
