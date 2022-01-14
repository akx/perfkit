import argparse
import itertools
import json
import statistics
import sys
from collections import defaultdict
from numbers import Number
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
                if initial_pcts[key] is not None
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


def get_grouped_datum(key_field: str, key_value, grouped: Dict[str, list]):
    grouped_datum = {key_field: key_value}
    for key, values in grouped.items():
        if all(isinstance(val, Number) for val in values):
            grouped_datum[f"{key}_mean"] = round(statistics.mean(values), 3)
            grouped_datum[f"{key}_median"] = statistics.median(values)
            grouped_datum[f"{key}_sum"] = sum(values)
        else:
            if len(set(values)) != 1:
                print(
                    f"{key_field}={key_value}: Multiple values for grouped non-number {key}: {values}"
                )
            grouped_datum[key] = values[0]
    return grouped_datum


def group_by(data: List[Dict[str, Any]], key_field: str):
    for group_key, group_data in itertools.groupby(data, lambda d: d.get(key_field)):
        grouped = defaultdict(list)
        for datum in group_data:
            for key, value in datum.items():
                if key == key_field:
                    continue
                grouped[key].append(value)
        yield get_grouped_datum(key_field, group_key, grouped)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove-time", action="store_true", default=False)
    ap.add_argument("--group-key", default=None)
    ap.add_argument("--pct-field", dest="pct_fields", action="append", default=[])
    ap.add_argument("--format", choices=("json", "gfm"), default="json")
    args = ap.parse_args()
    data = [
        flatten(json.loads(line), remove_time=args.remove_time) for line in sys.stdin
    ]
    if args.group_key:
        data = list(group_by(data, args.group_key))
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
