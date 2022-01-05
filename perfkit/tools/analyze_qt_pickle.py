import pickle
import sys
from collections import Counter


def main():
    with open(sys.argv[1], "rb") as outf:
        qt_data = pickle.load(outf)

    assert isinstance(qt_data, dict)
    assert qt_data["v"] == 1
    queries_by_section_and_stack = qt_data["qbss"]

    for section, data in queries_by_section_and_stack.items():
        if not section:
            continue
        print(f"# {section}")

        for (qry, stack), n in data.most_common(5):
            print(f"{n} / {qry}")
            print(stack)
            print("\n" * 5)


if __name__ == "__main__":
    main()
