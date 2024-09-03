import sys
import os
import csv

from servers.social_media_server import SimpleSocialMediaServer, MultiSocialMediaServer
from servers.master_server import MasterServer

if len(sys.argv) != 2:
    print(f'use: {os.path.basename(sys.executable)} {sys.argv[0]} <server>')
    exit(1)

server_name = sys.argv[1]

csv_filename = 'servers.csv'
server_dict: dict[str, tuple[str, int, str]]= {}

with open(csv_filename) as file:
    reader = csv.reader(file)
    _ = next(reader)

    try:
        for row in reader:
            server_dict[row[0]] = (row[1], int(row[2]), row[3])
    except:
        print(f'format error in file {csv_filename}')
        exit(1)

if server_name not in server_dict.keys():
    print(f'argument {server_name} is not in server list')
    exit(1)

ip = server_dict[server_name][0]
port = server_dict[server_name][1]
db = server_dict[server_name][2]

print(f'URL: {ip}:{port}')
print(f'database: {db}')

match server_name:
    case 'master':
        del server_dict[server_name]
        server = MasterServer(ip, port, server_dict)
    case 'others':
        server = MultiSocialMediaServer(ip, port, db)
    case _:
        server = SimpleSocialMediaServer(ip, port, db, server_name)

try:
    server.run()

except KeyboardInterrupt:
    server.close()
    print('\rserver shut down by keyboard interrupt.')

