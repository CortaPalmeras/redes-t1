import sqlite3
import typing

from . import query_validation as qv

DatabaseResult = list[str]

DatabaseError = str

DatabaseQueryHandler = typing.Callable[[qv.ValidQuery], DatabaseResult | DatabaseError]


def simple_query_handler(cursor: sqlite3.Cursor, social: str):

    def query_database(query: qv.ValidQuery) -> DatabaseResult | DatabaseError:
        result = cursor.execute(
            'SELECT handler FROM person WHERE fullname = ?',
            (query.name,)
        ).fetchall()

        if len(result) == 0:
            return DatabaseError("no result found for the specified person")

        else:
            result = typing.cast(list[tuple[str]], result)
            return DatabaseResult(social + ',' + result[0][0])

    return query_database


def multisocial_query_handler(cursor: sqlite3.Cursor):

    def query_multisocial_database(query: qv.ValidQuery) -> DatabaseResult | DatabaseError:
        if query.social == 'all':
            result = cursor.execute(
                'SELECT social, handler FROM person WHERE fullname = ?',
                (query.name,)
            ).fetchall()

        else:
            result = cursor.execute(
                'SELECT * FROM person WHERE fullname= ? AND social = ?',
                (query.name, query.social)
            ).fetchall()

        if len(result) == 0:
            return DatabaseError("no result found for the specified person")

        else:
            result = typing.cast(list[tuple[str,str]], result)
            data = [ ','.join(value) for value in result ]
            return DatabaseResult(data)

    return query_multisocial_database

