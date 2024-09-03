import csv
import sqlite3
import sys
import os

def format_name(fname: str, lname: str) -> str:
    return ' '.join(f'{fname} {lname}'.split()) \
    .lower() \
    .replace('ñ', 'n')  \
    .replace('á', 'a')  \
    .replace('é', 'e')  \
    .replace('í', 'i')  \
    .replace('ó', 'o')  \
    .replace('ú', 'u')  \

if len(sys.argv) != 2:
    print(f"use: {os.path.basename(sys.executable)} {sys.argv[0]} <csv file>")
    exit(1)


# crear directorio de datos
data_dirname = 'data'
if os.path.exists(data_dirname):
    if not os.path.isdir(data_dirname):
        print(f'error creating directory "{data_dirname}"')
        exit(1)
else:
    os.mkdir(path=data_dirname)

# leer lista de servidores
servers: dict[str, str] = {}
with open('servers.csv') as file:
    reader = csv.reader(file)
    _ = next(reader)

    for row in reader:
        servers[row[0]] = row[3]


# se elimina master y others
others_filename = servers['others']
del servers['master']
del servers['others']


# se crea la base de datos de others
others_db = sqlite3.connect(others_filename)
others_cur = others_db.cursor()
_ = others_cur.execute("DROP TABLE IF EXISTS person")
_ = others_cur.execute("CREATE TABLE person(fullname, social, handler, " \
                       + "CONSTRAINT person_pkey PRIMARY KEY (fullname, social))")


# se crea el resto de bases de datos
simple_servers = set(servers.keys())
databases = {key: sqlite3.connect(filename) for key, filename in servers.items()}
cursors = {key: db.cursor() for key, db in databases.items()}

for cur in cursors.values():
    _ = cur.execute("DROP TABLE IF EXISTS person")
    _ = cur.execute("CREATE TABLE person(fullname, handler, " \
                        + "CONSTRAINT person_pkey PRIMARY KEY (fullname))")


with open(sys.argv[1]) as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')
    _ = next(reader)

    for row in reader:
        if row[2] in simple_servers:
            _ = cursors[row[2]].execute("INSERT INTO person VALUES (?, ?)", 
                                        (format_name(row[0], row[1]), row[3]))
        else:
            _ = others_cur.execute("INSERT INTO person VALUES (?, ?, ?)",
                                   (format_name(row[0], row[1]), row[2], row[3]))


others_db.commit()
others_db.close()

for db in databases.values():
    db.commit()
    db.close()

