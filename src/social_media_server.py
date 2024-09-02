import socket as skt
import sqlite3

from .query_validation import *
from .databases import *

BUFFSIZE = 1024

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


