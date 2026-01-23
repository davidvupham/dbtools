# Part 1: Markdown basics

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Level](https://img.shields.io/badge/Level-Beginner-yellow)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](../quick-reference.md) | [Part 2: Intermediate](./series-part2-intermediate.md)

## Table of contents

- [Introduction](#introduction)
- [What is Markdown?](#what-is-markdown)
- [Getting started](#getting-started)
- [Headings](#headings)
- [Paragraphs and line breaks](#paragraphs-and-line-breaks)
- [Text formatting](#text-formatting)
- [Links](#links)
- [Images](#images)
- [Lists](#lists)
- [Code](#code)
- [Blockquotes](#blockquotes)
- [Horizontal rules](#horizontal-rules)
- [Putting it together: Your first README](#putting-it-together-your-first-readme)
- [Practice exercises](#practice-exercises)
- [Summary](#summary)
- [Next steps](#next-steps)

---

## Introduction

Welcome to the Markdown Mastery course. In this first part, you'll learn the core syntax that forms the foundation of all Markdown writing. By the end, you'll be able to create well-formatted documents, README files, and notes.

### What you'll learn

- Core Markdown syntax (CommonMark standard)
- How to format text, create links, and add images
- How to write structured documents with headings and lists
- How to include code in your documents

### Prerequisites

- A text editor (VS Code, Notepad++, or any plain text editor)
- Optionally: A Markdown previewer

[↑ Back to Table of Contents](#table-of-contents)

---

## What is Markdown?

Markdown is a lightweight markup language created by John Gruber in 2004. It allows you to write formatted text using simple, readable syntax that converts to HTML.

### Why Markdown matters

| Traditional Word Processor | Markdown |
|---------------------------|----------|
| Binary format (.docx) | Plain text (.md) |
| Requires specific software | Works in any text editor |
| Difficult to version control | Git-friendly |
| Format lock-in | Portable and future-proof |

### Where Markdown is used

- **GitHub/GitLab**: README files, issues, pull requests, wikis
- **Documentation**: MkDocs, Docusaurus, GitBook, Read the Docs
- **Note-taking**: Obsidian, Notion, Bear, Joplin
- **Communication**: Slack, Discord, Reddit, Stack Overflow
- **Blogging**: Jekyll, Hugo, Ghost

### The philosophy

Markdown's design goal is **readability**. A Markdown document should be readable as-is, without rendering. The syntax uses characters that visually suggest their meaning:

```markdown
# This looks like a heading
**This looks bold**
- This looks like a bullet point
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Getting started

### Setting up your environment

1. **Create a new file** with the `.md` extension (e.g., `learning.md`)
2. **Open it** in your text editor
3. **Enable preview** (if available):
   - **VS Code**: Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac)
   - **Online**: Use [StackEdit](https://stackedit.io/) or [Dillinger](https://dillinger.io/)

### Your first Markdown

Type this into your file:

```markdown
# Hello, Markdown!

This is my first Markdown document.

I'm learning to write **formatted text** without a word processor.
```

If you have a preview, you'll see:
- "Hello, Markdown!" as a large heading
- Regular paragraph text
- "formatted text" in bold

[↑ Back to Table of Contents](#table-of-contents)

---

## Headings

Headings create document structure. Use the `#` symbol followed by a space.

### Syntax

```markdown
# Heading 1 (largest)
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6 (smallest)
```

### Best practices

1. **Use only one H1** per document (the title)
2. **Don't skip levels** (e.g., don't go from H2 to H4)
3. **Use sentence case** (capitalize only the first word)
4. **Add a blank line** before and after headings

### Examples

```markdown
# Project documentation

## Installation

### Prerequisites

### Steps

## Usage

## Contributing
```

> [!TIP]
> Headings automatically create anchor links. `## Installation` becomes `#installation`, which you can link to with `[link](#installation)`.

### Common mistakes

```markdown
# Bad: No space after #
#Heading

# Bad: Inconsistent capitalization
## This Is Title Case (Don't Do This)

# Good: Sentence case with space
## This is sentence case
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Paragraphs and line breaks

### Paragraphs

Paragraphs are separated by **blank lines**:

```markdown
This is the first paragraph.

This is the second paragraph.
```

Text on consecutive lines becomes a single paragraph:

```markdown
This is all
one paragraph
even though it's
on multiple lines.
```

### Line breaks

To create a line break within a paragraph, end a line with **two spaces** or use `<br>`:

```markdown
First line
Second line (note: two spaces after "line")

Or use HTML:
First line<br>
Second line
```

### Best practice

Use blank lines between paragraphs rather than line breaks. Line breaks should be rare.

[↑ Back to Table of Contents](#table-of-contents)

---

## Text formatting

### Bold

Use double asterisks or double underscores:

```markdown
**bold text**
__also bold__
```

**Result:** **bold text**

### Italic

Use single asterisks or single underscores:

```markdown
*italic text*
_also italic_
```

**Result:** *italic text*

### Bold and italic

Combine them:

```markdown
***bold and italic***
___also works___
**_or mix them_**
```

**Result:** ***bold and italic***

### Strikethrough (GFM)

Use double tildes:

```markdown
~~deleted text~~
```

**Result:** ~~deleted text~~

### When to use formatting

| Style | Use For |
|-------|---------|
| **Bold** | Important terms, warnings, key concepts |
| *Italic* | Emphasis, introducing terms, titles of works |
| ~~Strikethrough~~ | Corrections, deprecated items |
| `Code` | Commands, file names, technical terms |

### Common mistakes

```markdown
# Bad: Spaces inside formatting
** not bold **
* not italic *

# Good: No spaces
**bold**
*italic*
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Links

Links are one of Markdown's most powerful features.

### Inline links

```markdown
[Link text](https://example.com)
```

**Result:** [Link text](https://example.com)

### Links with titles

Add a title that appears on hover:

```markdown
[Markdown Guide](https://www.markdownguide.org "The best Markdown reference")
```

### Reference-style links

Useful when you use the same URL multiple times:

```markdown
Check out [Markdown Guide][md-guide] for more information.
Also see their [basic syntax][md-guide] page.

[md-guide]: https://www.markdownguide.org
```

### Section links (anchors)

Link to headings in the same document:

```markdown
See the [Installation](#installation) section.
```

Rules for anchor links:
- Lowercase all letters
- Replace spaces with hyphens
- Remove punctuation

```markdown
## Getting Started Guide
<!-- Link: #getting-started-guide -->

## What's New?
<!-- Link: #whats-new -->
```

### Autolinks

Wrap URLs or emails in angle brackets:

```markdown
<https://www.example.com>
<contact@example.com>
```

### Best practices

1. **Use descriptive link text** (not "click here")
2. **Keep URLs readable** in reference-style when possible
3. **Test your links** before publishing

```markdown
# Bad
Click [here](https://example.com/docs) for documentation.

# Good
See the [project documentation](https://example.com/docs) for details.
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Images

Images use similar syntax to links, with an exclamation mark prefix.

### Basic syntax

```markdown
![Alt text](path/to/image.png)
```

### With title

```markdown
![Alt text](image.png "Image title")
```

### Reference-style images

```markdown
![Company logo][logo]

[logo]: /images/logo.png "Company Logo"
```

### Linked images

Make an image clickable:

```markdown
[![Alt text](thumbnail.png)](full-size.png)
```

### Image paths

| Path Type | Example | Use When |
|-----------|---------|----------|
| Relative | `./images/photo.png` | Images in your project |
| Absolute | `/docs/images/photo.png` | Images from project root |
| URL | `https://example.com/img.png` | External images |

### Best practices

1. **Always include alt text** for accessibility
2. **Use relative paths** for project images
3. **Store images** in an `images/` or `assets/` folder
4. **Use descriptive file names** (`architecture-diagram.png` not `img1.png`)

```markdown
# Bad
![](screenshot.png)

# Good
![Application login screen showing username and password fields](./images/login-screen.png)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Lists

### Unordered lists

Use `-`, `*`, or `+` followed by a space:

```markdown
- Item one
- Item two
- Item three
```

**Result:**
- Item one
- Item two
- Item three

### Ordered lists

Use numbers followed by a period and space:

```markdown
1. First step
2. Second step
3. Third step
```

**Result:**
1. First step
2. Second step
3. Third step

> [!NOTE]
> The actual numbers don't matter. Markdown renumbers automatically. This works:
> ```markdown
> 1. First
> 1. Second
> 1. Third
> ```

### Nested lists

Indent with 2-4 spaces:

```markdown
- Main item
  - Sub-item
  - Another sub-item
    - Deep nested
- Another main item
```

**Result:**
- Main item
  - Sub-item
  - Another sub-item
    - Deep nested
- Another main item

### Mixed lists

```markdown
1. First ordered item
   - Unordered sub-item
   - Another sub-item
2. Second ordered item
   1. Ordered sub-item
   2. Another ordered sub-item
```

### Lists with paragraphs

Indent content to keep it in the list:

```markdown
1. First item

   Additional paragraph for first item.

2. Second item
```

### When to use each type

| List Type | Use For |
|-----------|---------|
| Unordered (`-`) | Collections where order doesn't matter |
| Ordered (`1.`) | Steps, procedures, rankings |

[↑ Back to Table of Contents](#table-of-contents)

---

## Code

### Inline code

Use single backticks for code within text:

```markdown
Use the `print()` function to output text.
Run `npm install` to install dependencies.
```

**Result:** Use the `print()` function to output text.

### Fenced code blocks

Use triple backticks for multi-line code:

````markdown
```
function hello() {
    console.log("Hello, World!");
}
```
````

### Syntax highlighting

Specify the language after the opening backticks:

````markdown
```python
def greet(name):
    return f"Hello, {name}!"
```
````

**Result:**

```python
def greet(name):
    return f"Hello, {name}!"
```

### Common language identifiers

| Language | Identifier |
|----------|------------|
| Python | `python` |
| JavaScript | `javascript` or `js` |
| TypeScript | `typescript` or `ts` |
| Bash/Shell | `bash` or `shell` |
| SQL | `sql` |
| JSON | `json` |
| YAML | `yaml` |
| HTML | `html` |
| CSS | `css` |
| Markdown | `markdown` |
| Plain text | `text` |

### Indented code blocks

Indent with 4 spaces (older syntax):

```markdown
Regular paragraph.

    // This is a code block
    function example() {
        return true;
    }
```

> [!TIP]
> Prefer fenced code blocks with language identifiers over indented code blocks.

### Escaping backticks

To show backticks in inline code, use more backticks:

```markdown
`` `backticks` ``
```

**Result:** `` `backticks` ``

[↑ Back to Table of Contents](#table-of-contents)

---

## Blockquotes

Blockquotes are used for quotations, callouts, and highlighting text.

### Basic syntax

Prefix lines with `>`:

```markdown
> This is a blockquote.
> It can span multiple lines.
```

**Result:**

> This is a blockquote.
> It can span multiple lines.

### Multi-paragraph blockquotes

```markdown
> First paragraph.
>
> Second paragraph.
```

### Nested blockquotes

```markdown
> Main quote
>
> > Nested quote
> >
> > > Deeply nested
```

### Blockquotes with other elements

```markdown
> ## Heading in a quote
>
> - List item one
> - List item two
>
> **Bold text** and `code` work too.
```

### Use cases

- Quoting sources
- Highlighting important information
- Creating visual distinction
- Email-style replies

[↑ Back to Table of Contents](#table-of-contents)

---

## Horizontal rules

Create a visual separator with three or more hyphens, asterisks, or underscores:

```markdown
---

***

___
```

All produce the same result:

---

### Best practice

Use `---` consistently. Add blank lines before and after:

```markdown
## Section one

Content here.

---

## Section two

More content.
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Putting it together: Your first README

Let's create a complete README file using everything you've learned:

```markdown
# My Awesome Project

A brief description of what this project does and who it's for.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/project.git
   ```

2. Navigate to the project directory:
   ```bash
   cd project
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

## Usage

Import the module in your code:

```javascript
const awesome = require('my-awesome-project');

awesome.doSomething();
```

## Features

- **Fast**: Optimized for performance
- **Simple**: Easy to understand API
- **Flexible**: Works with any framework

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with love by [Your Name](https://github.com/username)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Practice exercises

### Exercise 1: Basic formatting

Create a document with:
- An H1 title
- Two H2 sections
- A paragraph with **bold** and *italic* text
- An unordered list with 3 items

### Exercise 2: Links and images

Create a document that includes:
- Three different external links
- One internal section link
- An image with proper alt text

### Exercise 3: Code documentation

Document a simple function:
- Use a heading for the function name
- Include inline code for parameter names
- Add a code block showing usage

### Exercise 4: Complete README

Create a README for a fictional project with:
- Project title and description
- Installation instructions (ordered list)
- Feature list (unordered)
- At least one code block
- A link to more documentation

[↑ Back to Table of Contents](#table-of-contents)

---

## Summary

In Part 1, you learned:

| Element | Syntax |
|---------|--------|
| Headings | `# H1` through `###### H6` |
| Bold | `**text**` |
| Italic | `*text*` |
| Links | `[text](url)` |
| Images | `![alt](url)` |
| Unordered list | `- item` |
| Ordered list | `1. item` |
| Inline code | `` `code` `` |
| Code block | ` ``` ` |
| Blockquote | `> quote` |
| Horizontal rule | `---` |

### Key principles

1. **Keep it simple**: Markdown is meant to be readable as plain text
2. **Be consistent**: Pick one style and stick to it
3. **Use blank lines**: Separate elements for clarity
4. **Always preview**: Check your formatting before publishing

[↑ Back to Table of Contents](#table-of-contents)

---

## Next steps

Continue to **[Part 2: Intermediate features](./series-part2-intermediate.md)** to learn:

- Tables
- Task lists
- Footnotes
- GitHub alerts and admonitions
- Emoji shortcodes
- Escaping special characters
- GitHub Flavored Markdown specifics

---

[↑ Back to Table of Contents](#table-of-contents)
