#!/usr/bin/env python3
"""
Insert minimal docstrings into pytest test functions across packages.

Targets:
- python/gds_snowflake/tests
- python/gds_vault/tests
- python/gds_postgres/tests

Rules:
- Add a one-line docstring as the first statement of any function whose name
  starts with "test_" and that currently has no docstring.
- Keep docstrings short to respect common 79-char line limits.
- Preserve existing formatting by inserting a single new line above the first
  statement of the function body (without rewriting the whole file).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Insertion:
    path: Path
    line: int  # 1-based line number to insert BEFORE
    indent: str
    text: str


def humanize_name(name: str) -> str:
    base = name.strip()
    # Remove "test_" prefix for readability
    if base.startswith("test_"):
        base = base[len("test_") :]
    return base.replace("_", " ")


def find_insertions_for_file(path: Path) -> List[Insertion]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []

    lines = src.splitlines()
    insertions: List[Insertion] = []

    def handle_func(node: ast.FunctionDef | ast.AsyncFunctionDef):
        if not node.name.startswith("test_"):
            return
        if ast.get_docstring(node) is not None:
            return  # already has a docstring
        if not node.body:
            return
        first_stmt = node.body[0]
        # Determine indentation from the first statement's current line
        first_line_idx = getattr(first_stmt, "lineno", None)
        if not isinstance(first_line_idx, int):
            return
        if first_line_idx - 1 < 0 or first_line_idx - 1 >= len(lines):
            return
        existing_line = lines[first_line_idx - 1]
        leading_len = len(existing_line) - len(existing_line.lstrip())
        indent = existing_line[:leading_len]
        # Compose docstring, keep it short
        desc = humanize_name(node.name)
        raw = f"Test: {desc}."
        # Enforce a conservative length to satisfy typical 79-char limits
        if len(raw) > 70:
            raw = raw[:67] + "..."
        doc = f'"""{raw}"""'
        insertions.append(
            Insertion(
                path=path,
                line=first_line_idx,
                indent=indent,
                text=doc,
            )
        )

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            handle_func(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            handle_func(node)
            self.generic_visit(node)

    Visitor().visit(tree)
    return insertions


def apply_insertions(path: Path, insertions: List[Insertion]) -> bool:
    if not insertions:
        return False
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    # Insert from bottom to top so line numbers remain valid
    changed = False
    for ins in sorted(insertions, key=lambda i: i.line, reverse=True):
        # Insert docstring line above the first statement
        lines.insert(ins.line - 1, f"{ins.indent}{ins.text}")
        changed = True
    if changed:
        new_src = "\n".join(lines) + ("\n" if src.endswith("\n") else "")
        path.write_text(new_src, encoding="utf-8")
    return changed


def main():
    root = Path(__file__).resolve().parents[1]
    target_dirs = [
        root / "gds_snowflake" / "tests",
        root / "gds_vault" / "tests",
        root / "gds_postgres" / "tests",
    ]

    total_files = 0
    total_insertions = 0
    for tdir in target_dirs:
        if not tdir.exists():
            continue
        for path in tdir.rglob("test_*.py"):
            total_files += 1
            ins = find_insertions_for_file(path)
            if not ins:
                continue
            if apply_insertions(path, ins):
                total_insertions += len(ins)

    print(f"Processed files: {total_files}")
    print(f"Docstrings inserted: {total_insertions}")


if __name__ == "__main__":
    main()
