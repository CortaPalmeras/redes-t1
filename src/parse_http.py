
def parse_http(self, message: str) -> ValidQuery | QueryError:
    header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
    method_string, _ = header.split(sep='\r\n', maxsplit=1)
    method, uri, _ = method_string.split(sep=' ', maxsplit=2)

    if method != 'GET':
        return QueryError(f'invalid method "{method}"')

    query_parts = uri.strip('/').split(sep='/')
    
    return self.validate_query(query_parts)
