import threading
import queue
import typing

T = typing.TypeVar('T')

TaskFunction = typing.Callable[[],T]
TaskQueue = queue.Queue[TaskFunction[T] | None]
ResultQueue = queue.Queue[T]

class ThreadPool(typing.Generic[T]):

    def __init__(self, size: int) -> None:
        self.threads: list[threading.Thread] = list()
        self.task_queue: TaskQueue[T] = queue.Queue()
        self.result_queue: ResultQueue[T] = queue.Queue()

        def work(task_queue: TaskQueue[T], result_queue: ResultQueue[T]) -> None:
            while True:
                task = task_queue.get()

                if task ==  None:
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

    def join_all(self) -> None:
        for _ in self.threads:
            self.task_queue.put(None)

        self.task_queue.join()

        for thread in self.threads:
            thread.join()

    def put_task(self, task: TaskFunction[T]) -> None:
        self.task_queue.put(task)

    def get_result(self) -> list[T]:
        self.task_queue.join()
        results: list[T] = []

        while not self.result_queue.empty():
            results.append(self.result_queue.get_nowait())

        return results


