import csv
import sqlite3
import sys
import os

if len(sys.argv) != 2:
    print(f"uso: python {sys.argv[0]} <archivo csv>")
    exit(1)

data_dirname = 'data'

if os.path.exists(data_dirname):
    if not os.path.isdir(data_dirname):
        print(f'no se puede crear directorio "{data_dirname}"')
        exit(1)
else:
    os.mkdir(path=data_dirname)

for filename in ['instagram.db', 'whatsapp.db', 'others.db']:
    filepath = f'{data_dirname}/{filename}'
    if os.path.exists(filepath):
        os.remove(filepath)


def format_name(fname: str, lname: str) -> str:
    return ' '.join(f'{fname} {lname}'.split()) \
    .lower() \
    .replace('ñ', 'n')  \
    .replace('á', 'a')  \
    .replace('é', 'e')  \
    .replace('í', 'i')  \
    .replace('ó', 'o')  \
    .replace('ú', 'u')  \

with open(sys.argv[1]) as file, \
    sqlite3.connect(f'{data_dirname}/instagram.db') as instagram, \
    sqlite3.connect(f'{data_dirname}/whatsapp.db') as whatsapp,   \
    sqlite3.connect(f'{data_dirname}/others.db') as others:

    _ = file.readline()
    reader = csv.reader(file, delimiter=',', quotechar='"')

    instagram_cur = instagram.cursor()
    whatsapp_cur = whatsapp.cursor()
    others_cur = others.cursor()

    _ = instagram_cur.execute("CREATE TABLE person(fullname, handler)")
    _ = whatsapp_cur.execute("CREATE TABLE person(fullname, handler)")
    _ = others_cur.execute("CREATE TABLE person(fullname, social, handler)")

    for row in reader:
        if row[2] == 'instagram':
            _ = instagram_cur.execute("INSERT INTO person VALUES (?, ?)", 
                                          (format_name(row[0], row[1]), row[3]))
        elif row[2] == 'whatsapp':
            _ = whatsapp_cur.execute("INSERT INTO person VALUES (?, ?)",
                                         (format_name(row[0], row[1]), row[3]))
        else:
            _ = others_cur.execute("INSERT INTO person VALUES (?, ?, ?)",
                                       (format_name(row[0], row[1]), row[2], row[3]))
    
    instagram.commit()
    whatsapp.commit()
    others.commit()


