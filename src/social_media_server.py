import socket as skt

IP = 'localhost'
PORT = 8080

BUFFSIZE = 1024

PersonQuery = tuple[str, list[str], str, str]

class SocialMediaServer:
    def __init__(self, 
                 social_media: set[str],
                 accepts_all: bool) -> None:
        self.social_media = social_media
        self.accepts_all = accepts_all

        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

    def open(self, ip: str, port: int):
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self):
        self.socket.close()

    def validate_query(self, query: PersonQuery) -> bool:
        return True

    def parse_http(self, message: str) -> PersonQuery | None:
        header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
        method_string, _ = header.split(sep='\r\n', maxsplit=1)
        method, uri, _ = method_string.split(sep=' ', maxsplit=2)

        if method != 'GET':
            return None

        query_parts = uri.split(sep='/')

        if len(query_parts) <= 4:
            return None

        social_media = query_parts[1]
        fnames = query_parts[2: -2]
        lname1 = query_parts[-2]
        lname2 = query_parts[-1]

        query = (social_media, fnames, lname1, lname2)

        return query if self.validate_query(query) else None

    def respond_success(self, con_socket: skt.socket, data: str) -> None:
        response = f'HTTP/1.1 200 OK\r\n\r\n{data}\r\n'
        _ = con_socket.send(response.encode())

    def respond_bad_request(self, con_socket: skt.socket) -> None:
        response = f'HTTP/1.1 400 BAD REQUEST\r\n\r\ninvalid query.\r\n'
        _ = con_socket.send(response.encode())

    def run(self) -> None:
        while True:
            connection = self.socket.accept()
            con_socket = connection[0]

            message = con_socket.recv(BUFFSIZE)

            query = self.parse_http(message.decode())

            if query != None:
                self.respond_success(con_socket, f"{query}")
            else:
                self.respond_bad_request(con_socket)

            con_socket.close()



