# Markdown glossary

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Markdown-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick-reference.md) | [Course Overview](./course-overview.md)

## Table of contents

- [Core concepts](#core-concepts)
- [Markdown flavors](#markdown-flavors)
- [Syntax elements](#syntax-elements)
- [Extended syntax](#extended-syntax)
- [Advanced features](#advanced-features)
- [Tools and software](#tools-and-software)
- [Formatting terminology](#formatting-terminology)
- [File types](#file-types)
- [Related standards](#related-standards)

---

## Core concepts

| Term | Definition |
|------|------------|
| **Markdown** | A lightweight markup language created by John Gruber in 2004 for formatting plain text documents |
| **Plain text** | Unformatted text that can be read by any text editor without special software |
| **Markup language** | A system for annotating text to define structure and formatting (e.g., HTML, XML, Markdown) |
| **Rendering** | The process of converting Markdown syntax into formatted output (usually HTML) |
| **Parser** | Software that reads Markdown and converts it to another format |

[↑ Back to Table of Contents](#table-of-contents)

## Markdown flavors

| Term | Definition |
|------|------------|
| **CommonMark** | The standardized specification of Markdown syntax, designed to resolve ambiguities in the original Markdown |
| **GFM (GitHub Flavored Markdown)** | GitHub's extended version of Markdown with additional features like tables, task lists, and strikethrough |
| **MultiMarkdown** | An extended Markdown variant supporting footnotes, tables, citations, and more |
| **R Markdown** | Markdown variant for R programming that can execute code and generate reports |
| **MDX** | Markdown with JSX support, allowing React components in Markdown documents |

[↑ Back to Table of Contents](#table-of-contents)

## Syntax elements

| Term | Definition |
|------|------------|
| **Heading** | A title or section header created with `#` symbols (H1-H6) |
| **Paragraph** | A block of text separated by blank lines |
| **Emphasis** | Italic (`*text*`) or bold (`**text**`) formatting |
| **Inline code** | Code within a paragraph, wrapped in backticks (`` `code` ``) |
| **Code block** | Multi-line code section, fenced with triple backticks (`` ``` ``) |
| **Blockquote** | Indented quotation created with `>` prefix |
| **List** | Ordered (numbered) or unordered (bulleted) items |
| **Link** | Clickable reference to another location, created with `[text](url)` syntax |
| **Image** | Embedded visual content, created with `![alt](url)` syntax |
| **Table** | Grid of data with rows and columns using pipe (`|`) syntax |
| **Horizontal rule** | A dividing line created with `---`, `***`, or `___` |

[↑ Back to Table of Contents](#table-of-contents)

## Extended syntax

| Term | Definition |
|------|------------|
| **Task list** | Checkable list items using `- [ ]` and `- [x]` syntax |
| **Footnote** | Reference note at the bottom of a document using `[^1]` syntax |
| **Definition list** | Term and definition pairs (supported by some parsers) |
| **Strikethrough** | Crossed-out text using `~~text~~` syntax |
| **Alert/Admonition** | Highlighted callout boxes using `> [!NOTE]` syntax |
| **Emoji shortcode** | Text codes like `:smile:` that render as emoji |
| **Autolink** | Automatic URL linking with `<https://url>` syntax |

[↑ Back to Table of Contents](#table-of-contents)

## Advanced features

| Term | Definition |
|------|------------|
| **Mermaid** | JavaScript library for creating diagrams from text descriptions in Markdown |
| **KaTeX** | Fast math typesetting library for rendering LaTeX equations |
| **LaTeX** | Typesetting system commonly used for mathematical notation |
| **PlantUML** | Tool for creating UML diagrams from plain text descriptions |
| **Front matter** | YAML metadata block at the beginning of a document (common in static site generators) |
| **Table of contents (TOC)** | Auto-generated list of headings with anchor links |

[↑ Back to Table of Contents](#table-of-contents)

## Tools and software

| Term | Definition |
|------|------------|
| **Pandoc** | Universal document converter supporting Markdown and many other formats |
| **Static site generator** | Software that builds websites from Markdown files (e.g., Jekyll, Hugo, MkDocs) |
| **Linter** | Tool that checks Markdown for style and syntax issues (e.g., markdownlint) |
| **WYSIWYG** | "What You See Is What You Get" - editors showing formatted output while typing |
| **Live preview** | Real-time rendering of Markdown as you type |

[↑ Back to Table of Contents](#table-of-contents)

## Formatting terminology

| Term | Definition |
|------|------------|
| **ATX headings** | Headings using `#` symbols (the standard style) |
| **Setext headings** | Headings using underlines of `=` or `-` (alternative style) |
| **Fenced code block** | Code block using triple backticks (`` ``` ``) |
| **Indented code block** | Code block using 4-space indentation |
| **Reference-style link** | Link defined separately with `[text][ref]` and `[ref]: url` |
| **Inline-style link** | Link with URL inline: `[text](url)` |
| **Alt text** | Alternative text for images, displayed if image fails to load |
| **Anchor** | Named location in a document for linking (auto-generated from headings) |

[↑ Back to Table of Contents](#table-of-contents)

## File types

| Extension | Description |
|-----------|-------------|
| `.md` | Standard Markdown file extension |
| `.markdown` | Alternative Markdown extension |
| `.mdx` | Markdown with JSX (React components) |
| `.Rmd` | R Markdown file |
| `.qmd` | Quarto Markdown file |

[↑ Back to Table of Contents](#table-of-contents)

## Related standards

| Term | Definition |
|------|------------|
| **HTML** | HyperText Markup Language - Markdown typically renders to HTML |
| **CSS** | Cascading Style Sheets - controls visual styling of rendered Markdown |
| **YAML** | Data serialization format used in front matter |
| **JSON** | Data format sometimes used for Markdown configuration |
| **XML** | Markup language; some Markdown extensions use XML-like syntax |

[↑ Back to Table of Contents](#table-of-contents)
