import argparse
import json
import sys
from typing import List, Any, Dict, Iterable


def flatten(datum: dict, *, remove_time: bool = False):
    datum = datum.copy()
    datum["commit"] = datum["commit"][:9]
    query_counts = datum.pop("query_counts", {})
    times = datum.pop("times", {})
    gauges = datum.pop("gauges", {})
    for key, count in query_counts.items():
        if key:
            datum[f"{key}_queries"] = count
    datum["total_queries"] = sum(query_counts.values(), 0)
    for key, duration in times.items():
        if key:
            datum[f"{key}_time"] = round(duration, 2)
    for key, value in gauges.items():
        if key:
            datum[f"{key}"] = value
    if remove_time:
        datum.pop("time", None)
    return datum


def compute_pcts(data, fields: List[str]):
    initial_pcts = {key: data[0].get(key) for key in fields}
    for datum in data:
        yield {
            **datum,
            **{
                f"{key}_%": round(datum.get(key) / initial_pcts[key], 3)
                for key in fields
            },
        }


def get_keys_in_order(dicts: Iterable[Dict[str, Any]]) -> List[str]:
    seen = set()
    keys = []
    for d in dicts:
        new_keys = [k for k in d if k not in seen]
        if new_keys:
            keys.extend(new_keys)
            seen.update(new_keys)
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove-time", action="store_true", default=False)
    ap.add_argument("--pct-field", dest="pct_fields", action="append", default=[])
    ap.add_argument("--format", choices=("json", "gfm"), default="json")
    args = ap.parse_args()
    data = [
        flatten(json.loads(line), remove_time=args.remove_time) for line in sys.stdin
    ]
    data = list(compute_pcts(data, fields=args.pct_fields))
    if args.format == "gfm":
        keys = get_keys_in_order(data)
        print(f"| {' | '.join(map(str, keys))} |")
        print(f"| {' | '.join(['---'] * len(keys))} |")
        for d in data:
            print(f"| {' | '.join(str(d.get(key, '')) for key in keys)} |")

    elif args.format == "json":
        print(json.dumps(data, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
