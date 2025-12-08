#!/usr/bin/env python3
"""
Validate Python code blocks found in the OOP tutorial markdown files.

For each markdown file beneath docs/tutorials/oop, this script extracts
```python``` fenced blocks and executes them sequentially within a fresh
module namespace. Execution stops per block when an exception is raised and
reports the failure alongside the snippet that triggered it.

Usage:
    python scripts/validate_oop_docs.py

    Optional arguments:
        --root PATH   Override the docs root (defaults to docs/tutorials/oop)
        --verbose     Print progress information for each block executed.

Exit status is non-zero if any block fails.
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
import traceback
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

CODE_FENCE_PATTERN = re.compile(
    r"```(?P<lang>python|py|python3)\s*\n(?P<code>.*?)```",
    re.IGNORECASE | re.DOTALL,
)

SKIP_HINTS = (
    "snowflake.connector",
    "# you don't need to run this",
    "from snowflake",
    "gds_snowflake",
    "__init__.py",
    "# test_",
    "# todo",
    "pytest.main",
    "from book import book",
    "multiple inheritance example",
)


@dataclass
class CodeBlock:
    path: Path
    index: int
    code: str
    start: int
    end: int

    @property
    def identifier(self) -> str:
        return f"{self.path}:{self.index}"


def iter_code_blocks(path: Path) -> Iterable[CodeBlock]:
    text = path.read_text(encoding="utf-8")
    for idx, match in enumerate(CODE_FENCE_PATTERN.finditer(text), start=1):
        code = match.group("code")
        start, end = match.span()
        yield CodeBlock(path=path, index=idx, code=code, start=start, end=end)


def should_skip(block: CodeBlock) -> bool:
    lowered = block.code.lower()
    return any(hint in lowered for hint in SKIP_HINTS)


def iter_markdown_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.md")):
        yield path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OOP tutorial code blocks.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("docs/tutorials/oop"),
        help="Path containing markdown files to validate.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress for each executed block.",
    )
    args = parser.parse_args(argv)

    root = args.root
    if not root.exists():
        parser.error(f"Root path does not exist: {root}")

    failures: list[tuple[CodeBlock, str]] = []

    for md_file in iter_markdown_files(root):
        # Maintain a shared namespace per file to mirror tutorial flow.
        file_namespace = {"__name__": "__main__", "__file__": str(md_file)}
        for block in iter_code_blocks(md_file):
            code = textwrap.dedent(block.code).strip()
            if not code:
                continue
            if should_skip(block):
                if args.verbose:
                    print(f"[skip] {block.identifier}")
                continue
            if args.verbose:
                print(f"[exec] {block.identifier}")
            try:
                compiled = compile(code, filename=str(md_file), mode="exec")
                exec(compiled, file_namespace)
            except Exception as exc:
                failure = "".join(traceback.format_exception(exc.__class__, exc, exc.__traceback__))
                failures.append((block, failure))

    if failures:
        print("Validation failed for the following blocks:\n")
        for block, failure in failures:
            print(f"- {block.identifier}")
            print("  Code snippet:")
            preview = textwrap.indent(
                textwrap.shorten(block.code.strip().replace("\n", " "), width=200),
                prefix="    ",
            )
            print(preview)
            print("  Traceback:")
            print(textwrap.indent(failure, prefix="    "))
        return 1

    if args.verbose:
        print("All code blocks executed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
