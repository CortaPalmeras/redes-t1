import threading
import queue 
import typing

TaskFunction = typing.Callable[[],str]
TaskQueue = queue.Queue[TaskFunction | None]
ResultQueue = queue.Queue[str]

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

class WorkerThreadPool:
    def __init__(self, size: int) -> None:
        self.threads: list[threading.Thread] = list()
        self.task_queue: TaskQueue = queue.Queue()
        self.result_queue: ResultQueue = queue.Queue()

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

