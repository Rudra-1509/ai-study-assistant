import time
from contextlib import contextmanager

class PipelineTimer:
    def __init__(self):
        self.results = {}

    @contextmanager
    def measure(self, name):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.results[name] = (time.perf_counter() - start)