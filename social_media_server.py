import socket as skt
import sqlite3
from typing import cast

BUFFSIZE = 1024

class ValidQuery:
    def __init__(self, name: str, social:str):
        self.name = name
        self.social = social

class QueryError:
    def __init__(self, value: str) -> None:
        self.value = value

DatabaseResult = list[str]

class DatabaseError:
    def __init__(self, value: str) -> None:
        self.value = value

def valid_name(name: str):
    return name.islower() and name.isalpha() and name.isascii()

class SocialMediaServer():
    def __init__(self, data: str) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.con = sqlite3.connect(data)
        self.cur = self.con.cursor()

    def open(self, ip: str, port: int) -> None:
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self) -> None:
        self.socket.close()

    def validate_query(self, query_parts: list[str]) -> ValidQuery | QueryError:
        if len(query_parts) < 3:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        for name in query_parts:
            if not valid_name(name):
                return QueryError(f'name "{name}" contains an invalid character.')

        return ValidQuery(' '.join(query_parts), 'all')

    def parse_http(self, message: str) -> ValidQuery | QueryError:
        header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
        method_string, _ = header.split(sep='\r\n', maxsplit=1)
        method, uri, _ = method_string.split(sep=' ', maxsplit=2)

        if method != 'GET':
            return QueryError(f'invalid method "{method}"')

        query_parts = uri.strip('/').split(sep='/')
        
        return self.validate_query(query_parts)

    def query_database(self, query: ValidQuery) -> DatabaseResult | DatabaseError:
        result = self.cur.execute('SELECT * FROM person WHERE fullname = ?', (query.name,)).fetchall()
        if len(result) == 0:
            return DatabaseError("no result found for the specified person")
        else:
            result = cast(list[tuple[str,str]], result)
            data = [ ','.join(value) for value in result ]
            return DatabaseResult(data)

    def respond_success(self, con_socket: skt.socket, data: DatabaseResult) -> None:
        data_as_csv = '\r\n'.join(data)
        response = f'HTTP/1.1 200 OK\r\n\r\n{data_as_csv}\r\n'
        _ = con_socket.send(response.encode())

    def respond_bad_request(self, con_socket: skt.socket, error: QueryError) -> None:
        response = f'HTTP/1.1 400 BAD REQUEST\r\n\r\n{error.value}\r\n'
        _ = con_socket.send(response.encode())

    def respond_not_found(self, con_socket: skt.socket, error: DatabaseError) -> None:
        response = f'HTTP/1.1 404 NOT FOUND\r\n\r\n{error.value}\r\n'
        _ = con_socket.send(response.encode())

    def run(self) -> None:
        while True:
            connection = self.socket.accept()
            con_socket = connection[0]

            message = con_socket.recv(BUFFSIZE)

            query = self.parse_http(message.decode())

            if isinstance(query, QueryError):
                self.respond_bad_request(con_socket, query)
            else:
                data = self.query_database(query)
                if isinstance(data, DatabaseError):
                    self.respond_not_found(con_socket, data)
                else:
                    self.respond_success(con_socket, data)

            con_socket.close()


class MultiSocialMediaServer(SocialMediaServer):
    def __init__(self, data: str) -> None:
        super().__init__(data)
        db_socials = self.cur.execute('SELECT DISTINCT social FROM person').fetchall()
        db_socials = cast(list[tuple[str]], db_socials)
        self.socials: set[str] = { social[0] for social in db_socials }

    def query_database(self, query: ValidQuery) -> DatabaseResult | DatabaseError:
        if query.social == 'all':
            return super().query_database(query)

        result = self.cur.execute(
            'SELECT * FROM person WHERE fullname= ? AND social = ?',
            (query.name, query.social)
        ).fetchall()

        if len(result) == 0:
            return DatabaseError("no result found for the specified person and social media pair")
        else:
            result = cast(list[tuple[str,str]], result)
            data = [ ','.join(value) for value in result ]
            return DatabaseResult(data)

    def validate_query(self, query_parts: list[str]) -> ValidQuery | QueryError:
        social = query_parts[0]
        names = query_parts[1:]

        if social != 'all' and social not in self.socials:
            return QueryError(f'requested plataform "{social}" not in the list of allowed plataforms:\n{self.socials}')

        name_validation = super().validate_query(names)

        if isinstance(name_validation, QueryError):
            return name_validation

        return ValidQuery(name_validation.name, social) 

