import os
import re
from pathlib import Path

DOCS_ROOT = Path("docs").resolve()

def check_link(file_path: Path, link: str) -> str | None:
    link = link.strip()
    if not link:
        return None
    if link.startswith("http") or link.startswith("https") or link.startswith("mailto:"):
        return None
    
    # Handle anchors
    path_part = link.split("#")[0]
    anchor_part = link.split("#")[1] if "#" in link else None

    if not path_part:
        # Just an anchor on same page #section
        return None

    # Resolve path
    # If it starts with /, it's usually relative to repo root or doc root. 
    # But in markdown usually relative to file. 
    # Check if absolute path (rare in md)
    if link.startswith("/"):
        # Assuming relative to git root which is CWD?
        target = (Path(os.getcwd()) / link.lstrip("/")).resolve()
    else:
        target = (file_path.parent / path_part).resolve()
    
    if not target.exists():
        return f"BROKEN: {link} (resolved: {target})"
    
    return None

def main():
    # Regex to capture [text](url)
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    broken_count = 0
    
    print(f"Scanning {DOCS_ROOT} for broken links...")
    
    for root, dirs, files in os.walk(DOCS_ROOT):
        for file in files:
            if not file.endswith(".md"):
                continue
            
            file_path = Path(root) / file
            try:
                content = file_path.read_text()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            for match in link_pattern.finditer(content):
                link = match.group(1)
                # Strip title if present: [text](url "title")
                # Also handle spaces encoded? usually md links don't have spaces unless %20
                # But simple split() handles "title" separation
                parts = link.split()
                if not parts: 
                    continue
                clean_link = parts[0]
                
                # Cleanup parens if regex was too greedy or balanced parens issue
                # minimal validation for now
                if clean_link.endswith(")"):
                    clean_link = clean_link[:-1]

                error = check_link(file_path, clean_link)
                if error:
                    # Filter out some known "template" or "example" broken links if strictly necessary
                    # but for now report all.
                    print(f"File: {file_path}")
                    print(f"  {error}")
                    broken_count += 1

    if broken_count == 0:
        print("✅ No broken relative links found.")
    else:
        print(f"❌ Found {broken_count} broken links.")

if __name__ == "__main__":
    main()
