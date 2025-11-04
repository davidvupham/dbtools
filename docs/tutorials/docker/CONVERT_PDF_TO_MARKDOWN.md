# Convert PDFs to HTML and Markdown (layout‑preserving)

This guide shows two ways to convert any PDF into Markdown that closely matches the original layout by going through HTML first. The Dockerized approach avoids installing tools on your host.

- Input: a PDF (e.g., `my_book.pdf`)
- Output: `my_book.md` plus per‑page images (e.g., `out001.png`)
- Location in this repo: use the `docs/tutorials/docker/resources/` folder (gitignored)

---

## Option A — Dockerized conversion (recommended)

This runs the conversion in a container that has the right tools preinstalled.

1) Build the converter image (done once):

```bash
docker build -t pdf2md-tool:latest \
  -f docs/tutorials/docker/resources/Dockerfile.convert \
  docs/tutorials/docker/resources
```

2) Place your PDF in the resources folder:

```bash
cp /path/to/my_book.pdf docs/tutorials/docker/resources/
```

3) Run the conversion (keeps images for faithful rendering):

```bash
docker run --rm \
  -v "$(pwd)/docs/tutorials/docker/resources":/work \
  pdf2md-tool:latest \
  "pdftohtml -c -hidden -nomerge -s my_book.pdf out && \
   pandoc -f html -t gfm --wrap=none -o my_book.md out-html.html && \
   echo DONE"
```

- This produces `my_book.md` plus `out001.png`, `out002.png`, … in the same folder.
- The generated Markdown contains lightweight HTML blocks and references page images to preserve layout.

---

## Option B — Host tools + helper script

Install tools on your machine (Linux example shown) and use the helper script.

1) Install tools:

```bash
sudo apt update
sudo apt install -y poppler-utils pandoc
```

2) Place your PDF and run the script:

```bash
cd docs/tutorials/docker/resources
bash convert_pdf_to_md.sh my_book.pdf my_book.md
```

- The script calls `pdftohtml` (producing `out-html.html` and images) and then `pandoc` to create `my_book.md`.
- Images are kept so the Markdown renders nearly like the PDF.

---

## What to expect

- Markdown fidelity: This approach preserves visual structure much better than plain text. You’ll see:
  - Headings and lists approximated via HTML+Markdown
  - Inline HTML blocks for precise positioning
  - Referenced per‑page images for backgrounds/graphics
- Output size: The `.md` can be large because it references page images.
- Portability: Most Markdown renderers will display the HTML blocks and images correctly.

---

## Troubleshooting

- Tools not found
  - Use the Dockerized method, or install `poppler-utils` (for `pdftohtml`) and `pandoc` via your package manager.
- No `out-html.html` generated
  - Ensure you passed a base name to `pdftohtml` (we use `out`), and then point pandoc at `out-html.html` (note the exact name).
- Missing images in the rendered Markdown
  - Make sure the image files (`outXXX.png`) are in the same folder as the Markdown file. Don’t move them without updating references.
- Scanned PDFs (image‑only)
  - These may yield image‑heavy output with little text structure. Consider OCR before conversion.

---

## Keep PDFs out of version control

- The `resources/` folder is gitignored to avoid committing copyrighted material.
- If you need to share small excerpts, extract brief quotes or summaries with attribution and add them to tracked docs outside `resources/`.

---

## Example

Convert the included `mastering_docker.pdf` (already in `resources/`):

```bash
# Dockerized
docker run --rm \
  -v "$(pwd)/docs/tutorials/docker/resources":/work \
  pdf2md-tool:latest \
  "pdftohtml -c -hidden -nomerge -s mastering_docker.pdf out && \
   pandoc -f html -t gfm --wrap=none -o mastering_docker.md out-html.html && \
   echo DONE"

# Or use the script (host tools)
cd docs/tutorials/docker/resources
bash convert_pdf_to_md.sh mastering_docker.pdf mastering_docker.md
```
