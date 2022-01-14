import datetime
import json
from typing import Optional, Any, Dict

from perfkit.query_tracker import QueryTracker
from perfkit.stopwatch import Stopwatch
from perfkit.utils import get_git_commit


def write_jsonl_record(
    filename: str,
    *,
    stopwatch: Optional[Stopwatch] = None,
    query_tracker: Optional[QueryTracker] = None,
    gauges: Optional[Dict[str, Any]] = None,
):
    record = {
        "commit": get_git_commit(),
        "time": datetime.datetime.utcnow().isoformat(),
    }
    if stopwatch:
        record["times"] = stopwatch.durations
    if query_tracker:
        record["query_counts"] = query_tracker.counts
    if gauges:
        record["gauges"] = gauges
    with open(filename, "a", encoding="utf-8") as outf:
        print(json.dumps(record, sort_keys=True, default=str), file=outf)
