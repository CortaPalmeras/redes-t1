
ValidRequest = list[str]

RequestError = str

def parse_http(message: str) -> ValidRequest | RequestError:
    header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
    start_line, _ = header.split(sep='\r\n', maxsplit=1)
    method, uri, _ = start_line.split(sep=' ', maxsplit=2)

    if method != 'GET':
        return RequestError(f'invalid method "{method}"')

    query_parts = uri.strip('/').split(sep='/')

    return ValidRequest(query_parts)

