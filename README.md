# perfkit

Bits and pieces for non-production performance observation, logging and optimization.

This has even less warranty or stability guarantees than usual.

## Rudimentary example usage for a Django app

NB: At present you'll need to manually patch 
    `django.db.backends.utils.CursorDebugWrapper`'s `logging.debug()` call 
    to include `stack_info=True` for stacks to get reported.

```python
from perfkit.patches import disable_linecache_checks
from perfkit.query_tracker import QueryTracker
from perfkit.django.query_tracker import prepare_logging
from perfkit.record import write_jsonl_record
from perfkit.stopwatch import Stopwatch

def main():
    disable_linecache_checks()

    qt = QueryTracker()
    sw = Stopwatch()
    prepare_logging(qt, depropagate=True)

    with sw.section("total"):
        c = Client()
        with qt.section("start"), sw.section("start"):
            resp = c.post("/heavy-request/", data=42)
    
        with qt.section("stop"), sw.section("stop"):
            resp = c.post("/other-heavy-request/", data=resp["foo"])

    write_jsonl_record("benchmark-logs.jsonl", stopwatch=sw, query_tracker=qt)
    qt.dump_to_pickle_autoname("benchmark-queries")
```

Then, follow up with e.g.

```
python -m perfkit.format_record --remove-time --pct-field total_time --pct-field total_queries < benchmark-logs.jsonl
```

to reformat the JSONL file into something that is more easily chartable (WIP :-) ).
