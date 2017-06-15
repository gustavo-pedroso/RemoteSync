from server_synchronizer import ServerSynchronizer
import sys

if len(sys.argv) != 2:
    print('usage: <python3 sync_server <server_port>')
    exit(0)

port = int(sys.argv[1])
ss = ServerSynchronizer(port)
ss.get_connections()
