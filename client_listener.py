import os
import time
from client_synchronizer import ClientSynchronizer
import pickle


class ClientListener:

    def __init__(self, path_to_listen, server_address, server_port):
        self.path = path_to_listen
        self.server_address = server_address
        self.server_port = server_port
        self.state_record_file = os.getcwd()+'/state_record_file.pickle'

    def listen(self):
        if os.path.exists(self.state_record_file):
            f = open(self.state_record_file, 'rb')
            folder = pickle.load(f)
        else:
            folder = []

        content = []
        for file in folder:
            content.append(file[0])

        sync = ClientSynchronizer(self.server_address, self.server_port, content, n_threads=5)

        while True:
            temp = []
            content = []
            for root, dirs, files in os.walk(self.path, topdown=True):

                for name in files:
                    file_path = os.path.join(root, name)
                    change_time = os.stat(file_path).st_mtime_ns
                    temp.append((file_path, change_time))
                    content.append(file_path)

                for name in dirs:
                    folder_path = os.path.join(root, name)
                    change_time = os.stat(folder_path).st_mtime_ns
                    temp.append((folder_path, change_time))
                    content.append(folder_path)

            if folder != temp:
                folder = temp
                f = open(self.state_record_file, 'wb')
                pickle.dump(folder, f)
                sync.find_changes(content)

            time.sleep(1)
