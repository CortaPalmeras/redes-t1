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

    instagram_people: list[tuple[str, str]] = list()
    whatsapp_people: list[tuple[str, str]] = list()
    others_people: list[tuple[str, str, str]] = list()

    for row in reader:
        if row[2] == 'instagram':
            instagram_people.append((format_name(row[0], row[1]), row[3]))
        elif row[2] == 'whatsapp':
            whatsapp_people.append((format_name(row[0], row[1]), row[3]))
        else:
            others_people.append((format_name(row[0], row[1]), row[3], row[2]))

    instagram_cur = instagram.cursor()
    _ = instagram_cur.execute("CREATE TABLE person(fullname, handler)")
    _ = instagram_cur.executemany("INSERT INTO person VALUES (?, ?)", instagram_people)
    instagram.commit()

    whatsapp_cur = whatsapp.cursor()
    _ = whatsapp_cur.execute("CREATE TABLE person(fullname, handler)")
    _ = whatsapp_cur.executemany("INSERT INTO person VALUES (?, ?)", whatsapp_people)
    whatsapp.commit()

    others_cur = others.cursor()
    _ = others_cur.execute("CREATE TABLE person(fullname, andler, social)")
    _ = others_cur.executemany("INSERT INTO person VALUES (?, ?, ?)", others_people)
    others.commit()


