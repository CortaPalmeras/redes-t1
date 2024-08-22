import sqlite3

con = sqlite3.connect("social.db")

cur = con.cursor()
_ = cur.execute("DROP TABLE movie")

_ = cur.execute("CREATE TABLE movie(title, year, score)")

_ = cur.execute("""
    INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
""")

con.commit()


data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
]
_ = cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
con.commit()

