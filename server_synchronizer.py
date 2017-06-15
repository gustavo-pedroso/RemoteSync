import util
import constants as const
import _thread
import os
import threading
import socket

threadLock = threading.Lock()


class ServerSinchronizer:

    def __init__(self, port):
        self.port = port
        self.user_home = os.getcwd()+'/USER'

    def get_connections(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((socket.gethostname(), self.port))
        s.listen()
        while True:
            cs, ca = s.accept()
            _thread.start_new_thread(self.sync_handler, (cs, ))

    def sync_handler(self, cs):
        response = b''.join(recvall(cs))
        cs.close()
        payload = util.deserialize(response)

        mode = payload[0]
        size_in_chunks = payload[1]
        file = payload[2]
        mod_map = payload[3]

        local_folder, local_file = util.split_path(self.user_home, file)
        local_file_path = local_folder + '/' + local_file

        if mode == 'create':
            print('synchronizing ', file, '...')
            threadLock.acquire()
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)
            threadLock.release()
            fd = open(local_file_path, 'wb')

            for i in range(0, size_in_chunks):
                if i in mod_map:
                    fd.write(mod_map[i])

            fd.close()
            return

        if mode == 'delete':
            if const.delete_flag:
                print('deleting ', file, '...')
                try:
                    os.remove(local_file_path)
                except IOError:
                    pass
            return

        if mode == 'update':
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






