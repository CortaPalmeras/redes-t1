import socket as skt
import threading
import queue
import typing

class ValidQuery:
    def __init__(self, name: str, social:str):
        self.name = name
        self.social = social

class QueryError:
    def __init__(self, value: str) -> None:
        self.value = value

BUFFSIZE = 1024

TaskFunction = typing.Callable[[],str]
TaskQueue = queue.Queue[TaskFunction | None]
ResultQueue = queue.Queue[str]

class ThreadPool:
    def __init__(self, size: int) -> None:
        self.threads: list[threading.Thread] = list()
        self.task_queue: TaskQueue = queue.Queue()
        self.result_queue: ResultQueue = queue.Queue()

        def work(task_queue: TaskQueue, result_queue: ResultQueue) -> None:
            while True:
                task = task_queue.get()
                if task == None:
                    task_queue.task_done()
                    break
                else:
                    res = task()
                    result_queue.put(res)
                    task_queue.task_done()

        for _ in range(size):
            new_thread = threading.Thread(target=work, 
                                          args=(self.task_queue, self.result_queue))
            new_thread.start()
            self.threads.append(new_thread)

    def put_task(self, task: TaskFunction) -> None:
        self.task_queue.put(task)

    def get_result(self) -> list[str]:
        self.task_queue.join()
        results: list[str] = []

        while not self.result_queue.empty():
            results.append(self.result_queue.get_nowait())

        return results

    def stop(self) -> None:
        for _ in self.threads:
            self.task_queue.put(None)

        self.task_queue.join()


class MasterServer():
    def __init__(self, data: str) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.thread_pool = ThreadPool(2)

    def open(self, ip: str, port: int) -> None:
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self) -> None:
        self.socket.close()

    def validate_query(self, query_parts: list[str]) -> ValidQuery | QueryError:
        if len(query_parts) < 3:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        for name in query_parts:
            if not valid_name(name):
                return QueryError(f'name "{name}" contains an invalid character.')

        return ValidQuery(' '.join(query_parts), 'all')

    def parse_http(self, message: str) -> ValidQuery | QueryError:
        header, _ = message.split(sep="\r\n\r\n", maxsplit=1)
        method_string, _ = header.split(sep='\r\n', maxsplit=1)
        method, uri, _ = method_string.split(sep=' ', maxsplit=2)

        if method != 'GET':
            return QueryError(f'invalid method "{method}"')

        query_parts = uri.strip('/').split(sep='/')

        return self.validate_query(query_parts)
    
    def run(self) -> None:
        while True:
            connection = self.socket.accept()
            con_socket = connection[0]

            message = con_socket.recv(BUFFSIZE)

            query = self.parse_http(message.decode())




