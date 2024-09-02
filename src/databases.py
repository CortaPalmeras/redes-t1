import sqlite3
import typing

from . import query_validation as qv

DatabaseResult = list[str]

class DatabaseError(typing.NamedTuple):
    value: str

def query_database(query: qv.ValidQuery, cursor: sqlite3.Cursor) -> DatabaseResult | DatabaseError:
    result = cursor.execute('SELECT * FROM person WHERE fullname = ?', (query.name,)).fetchall()

    if len(result) == 0:
        return DatabaseError("no result found for the specified person")

    else:
        result = typing.cast(list[tuple[str,str]], result)
        data = [ ','.join(value) for value in result ]
        return DatabaseResult(data)

def query_database_multisocial(query: qv.ValidQuery, cursor: sqlite3.Cursor) -> DatabaseResult | DatabaseError:
    if query.social == 'all':
        return query_database(query, cursor)

    result = cursor.execute(
        'SELECT * FROM person WHERE fullname= ? AND social = ?',
        (query.name, query.social)
    ).fetchall()

    if len(result) == 0:
        return DatabaseError("no result found for the specified person and social media pair")
    else:
        result = typing.cast(list[tuple[str,str]], result)
        data = [ ','.join(value) for value in result ]
        return DatabaseResult(data)

