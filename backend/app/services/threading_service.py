import threading
from typing import List, Dict, Any, Callable

from concurrent.futures import ThreadPoolExecutor

class ThreadingService:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def run_in_parallel(self, func: Callable, args_list: List[tuple]) -> List[Any]:
        futures = [self.executor.submit(func, *args) for args in args_list]
        return [future.result() for future in futures]

    def start(self):
        # The executor is already started at initialization
        pass

    def stop(self):
        self.executor.shutdown(wait=True)

threading_service = ThreadingService()