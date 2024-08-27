import sqlite3

from .queries import PersonQuery

class SocialMediaDatabase:
    def __init__(self, file: str) -> None:
        self.con = sqlite3.connect(file)
        self.cur = con.cursor()

    def execute(self, query: PersonQuery):
        if query.social == 'all':
            result = self.cur.execute("SELECT ...")

        else:
            result = self.cur.execute("SELECT ...")

        return result

con = sqlite3.connect("social.db")

cur = con.cursor()

_ = cur.execute("DROP TABLE movie")

_ = cur.execute("CREATE TABLE movie(title, year, score)")

data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
]
_ = cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
con.commit()

