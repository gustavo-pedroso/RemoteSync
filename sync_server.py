from server_synchronizer import ServerSinchronizer
import sys

if len(sys.argv) != 2:
    print('usage: <python3 sync_server <server_port>')
    exit(0)

port = int(sys.argv[1])
ss = ServerSinchronizer(port)
ss.get_connections()
