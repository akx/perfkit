import datetime
import os
import pickle
from collections import Counter, defaultdict
from contextlib import contextmanager
from typing import Dict

from perfkit.utils import get_git_commit


class QueryTracker:
    def __init__(self) -> None:
        self.enabled = True
        self.queries_by_section_and_stack = defaultdict(Counter)
        self.current_section = ""

    def reset(self):
        self.queries_by_section_and_stack.clear()

    @property
    def count(self) -> int:
        return sum(self.counts().values())

    @property
    def combined_queries(self) -> Counter:
        c = Counter()
        for name, qbs in self.queries_by_section_and_stack.items():
            c.update(qbs)
        return c

    @property
    def counts(self) -> Dict[str, int]:
        return {
            name: sum(qbs.values())
            for (name, qbs) in self.queries_by_section_and_stack.items()
        }

    def record(self, query: str, trace: str) -> None:
        if not self.enabled:
            return
        self.queries_by_section_and_stack[self.current_section][(query, trace)] += 1

    @contextmanager
    def section(self, name: str):
        old_section = self.current_section
        self.current_section = name
        yield
        self.current_section = old_section

    def dump_to_pickle(self, filename: str) -> bool:
        if not self.queries_by_section_and_stack:
            return False
        with open(filename, "wb") as outf:
            pickle.dump(
                {"v": 1, "qbss": self.queries_by_section_and_stack},
                outf,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
            return True

    def dump_to_pickle_autoname(self, directory: str) -> bool:
        filename = f"qt_{datetime.datetime.now().isoformat().replace(':', '-')}-{get_git_commit()}.pickle"
        os.makedirs(directory, exist_ok=True)
        return self.dump_to_pickle(os.path.join(directory, filename))
