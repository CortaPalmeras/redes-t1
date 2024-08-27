import socket as skt

BUFFSIZE = 1024

class PersonQuery:
    def __init__(self, social:str, name: str):
        self.social = social
        self.name = name

class QueryError:
    def __init__(self, value: str) -> None:
        self.value = value

def valid_name(name: str):
    return name.islower() and name.isalpha() and name.isascii()

class SocialMediaServer():
    def __init__(self) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

    def open(self, ip: str, port: int) -> None:
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self) -> None:
        self.socket.close()

    def validate_query(self, query_parts: list[str]) -> PersonQuery | QueryError:
        if len(query_parts) < 3:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        for name in query_parts:
            if not valid_name(name):
                return QueryError(f'name "{name}" contains an invalid character.')

        return PersonQuery('all', ' '.join(query_parts))

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
        response = f'HTTP/1.1 400 BAD REQUEST\r\n\r\n{error.value}\r\n'
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
                self.respond_success(con_socket, f"{query.social}, {query.name}")

            con_socket.close()

class MultiSocialMediaServer(SocialMediaServer):
    def __init__(self, socials: set[str]) -> None:
        super().__init__()
        self.socials = socials

    def validate_query(self, query_parts: list[str]) -> PersonQuery | QueryError:
        social = query_parts[0]
        names = query_parts[1:]

        if social != 'all' and social not in self.socials:
            return QueryError(f'requested plataform "{social}" not in the list of allowed plataforms:\n{self.socials}')

        name_validation = super().validate_query(names)

        if isinstance(name_validation, QueryError):
            return name_validation

        return PersonQuery(social, name_validation.name) 

