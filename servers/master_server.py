import socket

from . import query_validation as qv
from . import http
from .thread_pool import ThreadPool

class ValidQuery:
    def __init__(self, name: str, social:str):
        self.name = name
        self.social = social

class QueryError:
    def __init__(self, value: str) -> None:
        self.value = value

class MasterServer():
    def __init__(self, ip: str, port: int, servers: dict[str, tuple[str, int, str]]) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

        self.servers = {key: (value[0], value[1]) for key, value in servers.items()}

        self.simple_servers = set(servers.keys())
        self.simple_servers.remove('others')

        self.pool_size = len(self.simple_servers)
        self.pool = ThreadPool[http.ValidResponse | http.HttpParseError](self.pool_size)

        self.query_validator = qv.master_query_validator

    def close(self) -> None:
        self.socket.close()
        self.pool.join_all()

    def query_servers(self, query: qv.ValidQuery) -> bytes:

        if query.social == 'all':
            for key in self.simple_servers:
                self.pool.put_task(http.async_http_request(self.servers[key], query.name))

            res_others = http.parse_response(http.request_http(self.servers['others'], '/all' + query.name))
            res_threads = self.pool.get_result()
            res_threads.append(res_others)

            response = ''
            for res in res_threads:
                if isinstance(res, http.HttpParseError):
                    print(res.error)
                    return http.internal_server_error('something went wrong')

                else:
                    match res.status_code:
                        case '200': response += res.body
                        case '404': continue
                        case '400': 
                            print(f'a child server returned bad request: {res.body}')
                            return http.bad_request(res.body)
                        case _:
                            print('got an invalid status code')
                            return http.internal_server_error('something went wrong')

            if response == '':
                print('child servers returned no results')
                return http.not_found('no result found for the specified person')

        elif query.social in self.simple_servers:
            response = http.request_http(self.servers[query.social], query.name)

        else:
            response  = http.request_http(self.servers['others'], '/all' + query.name)

        print(f'query returned:\n{response}')
        return http.success(response)


    def run(self) -> None:
        while True:
            con_socket, con_addr = self.socket.accept()

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

                response = self.query_servers(query)
                _ = con_socket.sendall(response)




