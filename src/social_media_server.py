import socket as skt
import sqlite3

from . import query_validation as qv
from . import databases as db
from . import http_parse as http

BUFFSIZE = 1024


def success(data: str) -> str:
    return f'HTTP/1.1 200 OK\r\n\r\n{data}\r\n'

def bad_request(error: str) -> str:
    return f'HTTP/1.1 400 BAD REQUEST\r\n\r\n{error}\r\n'

def not_found(error: str) -> str:
    return f'HTTP/1.1 404 NOT FOUND\r\n\r\n{error}\r\n'

def respond(con_socket: skt.socket, response: str) -> None:
    _ = con_socket.send(response.encode())
    con_socket.close()


class SocialMediaServer():
    def __init__(self, ip: str, port: int, data: str, social: str) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

        self.con = sqlite3.connect(data)
        self.cur = self.con.cursor()

        self.query_validator = qv.simple_query_validator()
        self.database_handler = db.simple_databse_handler(self.cur, social)

    def __del__(self):
        self.socket.close()
        self.cur.close()
        self.con.close()

    def run(self) -> None:
        while True:
            connection = self.socket.accept()
            con_socket = connection[0]

            message = con_socket.recv(BUFFSIZE)

            request = http.parse_http(message.decode())

            if isinstance(request, http.RequestError):
                respond(con_socket, bad_request(request))
                continue

            query = self.query_validator(request)
            if isinstance(query, qv.QueryError):
                respond(con_socket, bad_request(query))
                continue

            data = self.database_handler(query)

            if isinstance(data, db.DatabaseError):
                respond(con_socket, not_found(data))
                continue

            respond(con_socket, success(data[0]))


# class MultiSocialMediaServer(SocialMediaServer):
#     def __init__(self, data: str) -> None:
#         super().__init__(data)
#         db_socials = self.cur.execute('SELECT DISTINCT social FROM person').fetchall()
#         db_socials = cast(list[tuple[str]], db_socials)
#         self.socials: set[str] = { social[0] for social in db_socials }
