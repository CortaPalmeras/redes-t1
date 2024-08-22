import socket as skt
from abc import ABC, abstractmethod

from .database_queries import PersonQuery, QueryError, QueryValidator

IP = 'localhost'
PORT = 8080

BUFFSIZE = 1024

class SocialMediaServer(ABC):
    def __init__(self) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

    def open(self, ip: str, port: int) -> None:
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self) -> None:
        self.socket.close()

    @abstractmethod
    def validate_query(self, query_parts: list[str]) -> PersonQuery | QueryError:
        pass

    def parse_http(self, message: str) -> PersonQuery | QueryError:
        header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
        method_string, _ = header.split(sep='\r\n', maxsplit=1)
        method, uri, _ = method_string.split(sep=' ', maxsplit=2)

        if method != 'GET':
            return QueryError(f'invalid method "{method}"')

        query_parts = uri.strip('/').split(sep='/')
        
        return self.validate_query(query_parts)

    def respond_success(self, con_socket: skt.socket, data: str) -> None:
        response = f'HTTP/1.1 200 OK\r\n\r\n{data}\r\n'
        _ = con_socket.send(response.encode())

    def respond_bad_request(self, con_socket: skt.socket, error: QueryError) -> None:
        response = f'HTTP/1.1 400 BAD REQUEST\r\n\r\n{error.reason}\r\n'
        _ = con_socket.send(response.encode())

    def respond_not_found(self) -> None:
        pass

    def run(self) -> None:
        while True:
            connection = self.socket.accept()
            con_socket = connection[0]

            message = con_socket.recv(BUFFSIZE)

            query = self.parse_http(message.decode())

            if isinstance(query, QueryError):
                self.respond_bad_request(con_socket, query)
            else:
                self.respond_success(con_socket, f"{query.social}, {query.fnames}, {query.lnames}")

            con_socket.close()


class SingleSocialMediaServer(SocialMediaServer):
    def __init__(self, social: str) -> None:
        super().__init__()
        self.social = social
        self.validator = QueryValidator(socials={social}, allows_all=False)

    def validate_query(self, query_parts: list[str]) -> PersonQuery | QueryError:
        if len(query_parts) < 3:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        social = self.social
        fnames = query_parts[0: -2]
        lnames = query_parts[-2:]

        return self.validator.validate(social, fnames, lnames)

class MultiSocialMediaServer(SocialMediaServer):
    def __init__(self, socials: set[str]) -> None:
        super().__init__()
        self.socials = socials
        self.validator = QueryValidator(socials=socials, allows_all=True)

    def validate_query(self, query_parts: list[str]) -> PersonQuery | QueryError:
        if len(query_parts) < 4:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        social = query_parts[0]
        fnames = query_parts[1: -2]
        lnames = query_parts[-2:]

        return self.validator.validate(social, fnames, lnames)
        


