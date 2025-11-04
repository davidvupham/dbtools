from pathlib import Path
from pypdf import PdfReader

PDF = Path('/home/dpham/src/dbtools/docs/tutorials/docker/resources/mastering_docker.pdf')
OUT = Path('/home/dpham/src/dbtools/docs/tutorials/docker/resources/mastering_docker.txt')

if not PDF.exists():
    raise SystemExit(f'PDF not found: {PDF}')

reader = PdfReader(str(PDF))
texts = []
for i, page in enumerate(reader.pages):
    try:
        t = page.extract_text() or ''
    except Exception as e:
        t = f"\n[ERROR extracting page {i}: {e}]\n"
    texts.append(t)

OUT.write_text('\n\n==== PAGE BREAK ====\n\n'.join(texts))
print(f'Wrote {OUT} with {len(reader.pages)} pages')
