import socket as skt
import typing
import sqlite3

from . import query_validation as qv
from . import databases as db
from . import http

class AbstractSocialMediaServer():
    def __init__(self, ip: str, port: int, data: str) -> None:
        self.con = sqlite3.connect(data)
        self.cur = self.con.cursor()

        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

        self.query_validator: qv.QueryValidator
        self.database_handler: db.DatabaseHandler


    def close(self) -> None:
        self.socket.close()
        self.cur.close()
        self.con.close()

    def run(self) -> None:
        while True:
            con_socket, con_addr = self.socket.accept()
            print()

            with con_socket:
                message = con_socket.recv(http.BUFFSIZE)
                print(f'recieved request form {con_addr}')

                request = http.parse_http(message.decode())
                if isinstance(request, http.HttpParseError):
                    print(f'unable to parse request: {request.error}')
                    _ = con_socket.sendall(http.bad_request(request.error))
                    continue

                print(f'requested: {request.query}')

                query = self.query_validator(request.query)
                if isinstance(query, qv.QueryError):
                    print(f'query is invalid: {query.error}')
                    _ = con_socket.sendall(http.bad_request(query.error))
                    continue

                result = self.database_handler(query)
                if isinstance(result, db.DatabaseError):
                    print('query returned no reults')
                    _ = con_socket.sendall(http.not_found(result.error))
                    continue

                print(f'query returned:\n{result.data}')

                _ = con_socket.sendall(http.success(result.data))


class SimpleSocialMediaServer(AbstractSocialMediaServer):
    def __init__(self, ip: str, port: int, data: str, social: str) -> None:
        super().__init__(ip, port, data)
        
        self.query_validator = qv.simple_query_validator
        self.database_handler = db.simple_databse_handler(self.cur, social)


class MultiSocialMediaServer(AbstractSocialMediaServer):
    def __init__(self, ip: str, port: int, data: str) -> None:
        super().__init__(ip, port, data)

        db_socials = self.cur.execute('SELECT DISTINCT social FROM person').fetchall()
        db_socials = typing.cast(list[tuple[str]], db_socials)
        socials: set[str] = { social[0] for social in db_socials }

        self.query_validator = qv.multisocial_query_validator(socials)
        self.database_handler = db.multisocial_database_handler(self.cur)


