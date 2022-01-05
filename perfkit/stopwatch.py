import dataclasses
import time
from contextlib import contextmanager
from typing import List, Dict


@dataclasses.dataclass
class StopwatchRecord:
    start: float
    end: float
    name: str

    @property
    def duration(self):
        return self.end - self.start


class Stopwatch:
    def __init__(self):
        self.records: List[StopwatchRecord] = []

    def clock(self) -> float:
        return time.perf_counter()

    @property
    def total(self) -> float:
        return sum((r.duration for r in self.records), 0)

    @property
    def durations(self) -> Dict[str, float]:
        return {s.name: s.duration for s in self.records}

    @contextmanager
    def section(self, name: str):
        start = self.clock()
        yield
        end = self.clock()
        self.records.append(StopwatchRecord(start=start, end=end, name=name))
