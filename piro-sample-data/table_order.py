#!/usr/bin/env python3
"""
Produce an ordering of PIRO table DDL scripts that respects foreign key dependencies.
Falls back to filename order for any cycles or unparsed scripts.
"""

import re
import sys
from collections import defaultdict, deque
from pathlib import Path


CREATE_PATTERN = re.compile(r"CREATE\s+TABLE\s+\[?(?:dbo\.)?([^\]\s]+)\]?", re.IGNORECASE)
REFERENCES_PATTERN = re.compile(r"REFERENCES\s+\[?(?:dbo\.)?([^\]\s]+)\]?", re.IGNORECASE)


def load_scripts(directory):
    files = sorted(directory.glob("*.sql"))
    texts = {}
    for path in files:
        try:
            data = path.read_text(encoding="utf-16-le")
        except UnicodeError:
            data = path.read_text(encoding="utf-8", errors="ignore")
        texts[path] = data
    return files, texts


def extract_tables(files, texts):
    table_to_file = {}
    for path in files:
        match = CREATE_PATTERN.search(texts[path])
        if match:
            table_to_file[match.group(1).strip().lower()] = path
    return table_to_file


def build_dependency_graph(table_to_file, texts):
    deps = defaultdict(set)
    for table, path in table_to_file.items():
        for ref in REFERENCES_PATTERN.findall(texts[path]):
            ref_name = ref.strip().lower()
            if ref_name != table and ref_name in table_to_file:
                deps[table].add(ref_name)
    # Ensure every table key is present
    for table in table_to_file:
        deps.setdefault(table, set())
    return deps


def topo_sort(table_to_file, deps):
    indegree = {table: 0 for table in table_to_file}
    for table in table_to_file:
        for ref in deps[table]:
            indegree[table] += 1

    queue = deque(sorted([t for t, deg in indegree.items() if deg == 0]))
    ordered = []
    remaining = set(table_to_file)

    while queue:
        table = queue.popleft()
        ordered.append(table_to_file[table])
        remaining.discard(table)
        for other in list(remaining):
            if table in deps[other]:
                indegree[other] -= 1
                if indegree[other] == 0:
                    queue.append(other)
        queue = deque(sorted(queue))

    if remaining:
        # Append any cyclic/unresolved tables in filename order
        unresolved = sorted(table_to_file[t] for t in remaining)
        ordered.extend(unresolved)

    return ordered


def main():
    if len(sys.argv) != 2:
        print("Usage: table_order.py <table_directory>", file=sys.stderr)
        sys.exit(1)

    directory = Path(sys.argv[1])
    files, texts = load_scripts(directory)
    table_to_file = extract_tables(files, texts)
    deps = build_dependency_graph(table_to_file, texts)
    ordered_files = topo_sort(table_to_file, deps)

    ordered_set = set(ordered_files)
    for path in files:
        if path not in ordered_set:
            ordered_files.append(path)

    for path in ordered_files:
        print(path)


if __name__ == "__main__":
    main()
