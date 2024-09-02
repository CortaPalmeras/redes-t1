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
    sqlite3.connect(f'{data_dirname}/instagram.db') as insta_db, \
    sqlite3.connect(f'{data_dirname}/whatsapp.db') as whats_db,   \
    sqlite3.connect(f'{data_dirname}/others.db') as other_db:

    _ = file.readline()
    reader = csv.reader(file, delimiter=',', quotechar='"')

    insta_cur = insta_db.cursor()
    whats_cur = whats_db.cursor()
    other_cur = other_db.cursor()

    _ = insta_cur.execute("DROP TABLE IF EXISTS person")
    _ = whats_cur.execute("DROP TABLE IF EXISTS person")
    _ = other_cur.execute("DROP TABLE IF EXISTS person")

    _ = insta_cur.execute("CREATE TABLE person(fullname, handler, " \
                          + "CONSTRAINT person_pkey PRIMARY KEY (fullname))")
    _ = whats_cur.execute("CREATE TABLE person(fullname, handler, " \
                          + "CONSTRAINT person_pkey PRIMARY KEY (fullname))")
    _ = other_cur.execute("CREATE TABLE person(fullname, social, handler, " \
                          + "CONSTRAINT person_pkey PRIMARY KEY (fullname, social))")
    for row in reader:
        match row[2]:
            case 'instagram':
                _ = insta_cur.execute("INSERT INTO person VALUES (?, ?)", 
                                            (format_name(row[0], row[1]), row[3]))
            case 'whats_db':
                _ = whats_cur.execute("INSERT INTO person VALUES (?, ?)",
                                            (format_name(row[0], row[1]), row[3]))
            case _:
                _ = other_cur.execute("INSERT INTO person VALUES (?, ?, ?)",
                                        (format_name(row[0], row[1]), row[2], row[3]))
    insta_db.commit()
    whats_db.commit()
    other_db.commit()


