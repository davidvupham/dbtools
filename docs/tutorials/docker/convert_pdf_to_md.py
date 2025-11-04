from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
TXT = ROOT / "resources" / "mastering_docker.txt"
MD = ROOT / "resources" / "mastering_docker.md"

if not TXT.exists():
    raise SystemExit(f"Missing input text file: {TXT}")

raw = TXT.read_text(encoding="utf-8", errors="ignore")

# -----------------------------
# Normalization
# -----------------------------
text = raw.replace("\r\n", "\n").replace("\r", "\n")
text = text.replace("\u00a0", " ")
# Remove excessive null/zero-width chars that sometimes appear
text = text.replace("\u200b", "").replace("\ufeff", "")

# Our extractor inserted this marker between pages
pages = [p.strip() for p in text.split("==== PAGE BREAK ====")]

# Map odd bullet glyphs from the PDF to dashes
BULLET_GLYPHS = [
    "•", "◦", "▪", "–", "—", "·", "●", "○",
    "", "", "", "", "", "", "", "",
]


def normalize_bullets(line: str) -> str:
    s = line
    for g in BULLET_GLYPHS:
        s = s.replace(g + " ", "- ")
        if s.startswith(g):
            s = "- " + s[len(g):].lstrip()
    # Convert common patterns like "-  - " to single dash
    s = re.sub(r"^[-–—]\s+[-–—]\s+", "- ", s)
    return s


def is_probable_heading(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    # Chapter/Part markers
    if re.match(r"^(Chapter|Part)\b", t, re.IGNORECASE):
        return True
    # Short ALL CAPS lines (likely section titles)
    if (
        len(t) <= 80
        and t.replace(" ", "").isupper()
        and re.search(r"[A-Z]", t)
    ):
        return True
    # Lines that look like Title Case without trailing punctuation
    if len(t) <= 80 and t.endswith(":"):
        return True
    return False


_SPACED_LETTERS_RE = re.compile(
    r"(?:(?<=\s)|^)(?:[A-Za-z]\s){3,}[A-Za-z](?=(\s|$))"
)


def fix_spaced_letters(line: str) -> str:
    """Join sequences like 'd o c k e r' -> 'docker' to improve readability."""

    def _join(match: re.Match) -> str:
        return match.group(0).replace(" ", "")

    return _SPACED_LETTERS_RE.sub(_join, line)


def reflow_paragraphs(lines: list[str]) -> list[str]:
    """
    Join wrapped lines into paragraphs while preserving lists and headings.
    """
    out: list[str] = []
    buf: list[str] = []

    def flush_buf():
        nonlocal buf
        if buf:
            paragraph = " ".join(
                # If a line ends with a hyphen, join without extra space
                [re.sub(r"-\s*$", "", buf[0])] + buf[1:]
            )
            # Collapse multiple spaces
            paragraph = re.sub(r"\s{2,}", " ", paragraph).strip()
            out.append(paragraph)
            buf = []

    for raw_ln in lines:
        ln = normalize_bullets(raw_ln)
        ln = fix_spaced_letters(ln)
        t = ln.strip()

        if not t:
            flush_buf()
            out.append("")
            continue

        # Headings and list items flush the current paragraph
        if is_probable_heading(t) or re.match(r"^(-|\d+\.|[a-zA-Z]\))\s+", t):
            flush_buf()
            out.append(t)
            continue

        # Inside a paragraph: append, stripping hard wraps
        # Heuristic: if previous line ends with punctuation,
        # start new paragraph
        if buf and re.search(r"[\.!?:]$", buf[-1].strip()):
            flush_buf()
        buf.append(t)

    flush_buf()
    return out


def promote_headings(line: str) -> str:
    t = line.strip()
    if re.match(r"^(Chapter|Part)\b", t, re.IGNORECASE):
        return f"## {t}"
    # Convert ALL CAPS short lines to H3
    if (
        len(t) <= 80
        and t.replace(" ", "").isupper()
        and re.search(r"[A-Z]", t)
    ):
        return f"### {t.title()}"
    # Trailing colon as section header
    if len(t) <= 80 and t.endswith(":"):
        return f"### {t[:-1]}"
    return line


def process_page(block: str) -> str:
    lines = [ln.rstrip() for ln in block.split("\n")]
    lines = reflow_paragraphs(lines)
    # Promote headings
    out = [promote_headings(ln) for ln in lines]
    return "\n".join(out)


processed_pages = [process_page(p) for p in pages if p]
body = ("\n\n---\n\n").join(processed_pages)

header = "# Mastering Docker — Extracted Notes (auto-converted)\n\n"
MD.write_text(header + body, encoding="utf-8")
print(f"Wrote {MD}")
