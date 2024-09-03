import typing
import socket as skt

BUFFSIZE = 1024

class ValidRequest(typing.NamedTuple):
    query: list[str]

class HttpParseError(typing.NamedTuple):
    error: str

class ValidResponse(typing.NamedTuple):
    status_code: str
    body: str

def parse_http(message: str) -> ValidRequest | HttpParseError:
    try:
        header = message.split(sep='\r\n\r\n', maxsplit=1)[0]
        start_line = header.split(sep='\r\n', maxsplit=1)[0]
        method, path = start_line.split(sep=' ', maxsplit=2)[:2]

        if method != 'GET':
            return HttpParseError(f'invalid method "{method}"')

        query = path.strip('/').split(sep='/')

        return ValidRequest(query)

    except:
        return HttpParseError('unable to parse request')


def success(data: str) -> bytes:
    return f'HTTP/1.1 200 OK\r\n\r\n{data}\n'.encode()

def bad_request(error: str) -> bytes:
    return f'HTTP/1.1 400 Bad Request\r\n\r\n{error}\n'.encode()

def not_found(error: str) -> bytes:
    return f'HTTP/1.1 404 Not Found\r\n\r\n{error}\n'.encode()

def internal_server_error(error: str) -> bytes:
    return f'HTTP/1.1 500 Internal Server Error\r\n\r\n{error}\n'.encode()

def request_http(addres: tuple[str, int], path: str) -> str:
    request = f'GET {path} HTTP/1.1\r\n\r\n'
    with skt.create_connection(addres) as connection:
        connection.sendall(request.encode())
        result = connection.recv(BUFFSIZE).decode()
        return result

def parse_response(response: str) -> ValidResponse | HttpParseError:
    try:
        header, body = response.split(sep='\r\n\r\n', maxsplit=1)
        start_line = header.split(sep='\r\n', maxsplit=1)[0]
        status_code = start_line.split(sep=' ', maxsplit=2)[1]

        if not status_code.isnumeric():
            return HttpParseError(f'invalid status code {status_code}')

        return ValidResponse(status_code, body)

    except:
        return HttpParseError('unable to parse response')

def async_http_request(addres: tuple[str, int], path: str) -> typing.Callable[[], ValidResponse | HttpParseError]:
    return lambda: parse_response(request_http(addres, path))



