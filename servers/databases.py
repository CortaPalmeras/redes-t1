import sqlite3
import typing

from . import query_validation as qv

class DatabaseResult(typing.NamedTuple):
    data:str

class DatabaseError(typing.NamedTuple):
    error: str

DatabaseHandler = typing.Callable[[qv.ValidQuery], DatabaseResult | DatabaseError]


def simple_databse_handler(cursor: sqlite3.Cursor, social: str) -> DatabaseHandler:

    def query_database(query: qv.ValidQuery) -> DatabaseResult | DatabaseError:
        result = cursor.execute(
            'SELECT handler FROM person WHERE fullname = ?',
            (query.name,)
        ).fetchall()

        if len(result) == 0:
            return DatabaseError('no result found for the specified person')

        else:
            result = typing.cast(list[tuple[str]], result)
            return DatabaseResult(social + ',' + result[0][0])

    return query_database


def multisocial_database_handler(cursor: sqlite3.Cursor) -> DatabaseHandler:

    def query_multisocial_database(query: qv.ValidQuery) -> DatabaseResult | DatabaseError:
        if query.social == 'all':
            result = cursor.execute(
                'SELECT social, handler FROM person WHERE fullname = ?',
                (query.name,)
            ).fetchall()

        else:
            result = cursor.execute(
                'SELECT social, handler FROM person WHERE fullname= ? AND social = ?',
                (query.name, query.social)
            ).fetchall()

        if len(result) == 0:
            return DatabaseError('no result found for the specified person')

        else:
            result = typing.cast(list[tuple[str,str]], result)
            data = [ value[0] + ',' + value[1] for value in result ]
            return DatabaseResult('\n'.join(data))

    return query_multisocial_database

