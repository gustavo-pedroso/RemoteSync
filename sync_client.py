from client_listener import ClientListener
import sys

if len(sys.argv) != 4:
    print('usage: <python3 sync_client <root_sync_folder> <server_address> <server_port>')
    exit(0)
rootDir = sys.argv[1]
server_address = sys.argv[2]
server_port = int(sys.argv[3])

print('synchronizing:', rootDir, 'with server:', server_address, 'in port:', server_port)

cl = ClientListener(rootDir, server_address, server_port)
cl.listen()
