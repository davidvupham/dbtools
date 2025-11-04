#!/usr/bin/env bash
set -euo pipefail

# Convert a PDF to HTML (layout-preserving) and then to Markdown.
# Requires: pdftohtml (poppler-utils) and pandoc
# Usage: ./convert_pdf_to_md.sh mastering_docker.pdf mastering_docker.md

PDF_IN=${1:-mastering_docker.pdf}
MD_OUT=${2:-mastering_docker.md}
HTML_BASE=out

if ! command -v pdftohtml >/dev/null 2>&1; then
  echo "Error: pdftohtml not found. Please install poppler-utils (e.g., sudo apt install -y poppler-utils)" >&2
  exit 127
fi
if ! command -v pandoc >/dev/null 2>&1; then
  echo "Error: pandoc not found. Please install pandoc (e.g., sudo apt install -y pandoc)" >&2
  exit 127
fi

if [[ ! -f "$PDF_IN" ]]; then
  echo "Error: input PDF not found: $PDF_IN" >&2
  exit 1
fi

# Generate a single HTML file (plus images) with layout preserved
pdftohtml -c -hidden -nomerge -s "$PDF_IN" "$HTML_BASE" >/dev/null 2>&1 || {
  echo "pdftohtml failed" >&2
  exit 2
}

# pdftohtml names the file as '<base>-html.html'
HTML_FILE="${HTML_BASE}-html.html"

# Convert HTML to GitHub-Flavored Markdown without hard wrapping
pandoc -f html -t gfm --wrap=none -o "$MD_OUT" "$HTML_FILE" || {
  echo "pandoc conversion failed" >&2
  exit 3
}

# Keep images alongside the Markdown so it renders faithfully.
# Optionally uncomment next line to remove the intermediate HTML/CSS only.
# rm -f "$HTML_FILE" "${HTML_BASE}.css"

echo "Wrote $MD_OUT"
