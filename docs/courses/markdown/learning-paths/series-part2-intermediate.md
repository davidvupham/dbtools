# Part 2: Intermediate features

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Level](https://img.shields.io/badge/Level-Intermediate-orange)

> [!IMPORTANT]
> **Related Docs:** [Part 1: Basics](./series-part1-basics.md) | [Part 3: Advanced](./series-part3-advanced.md) | [Quick Reference](../quick_reference.md)

## Table of contents

- [Introduction](#introduction)
- [Tables](#tables)
- [Task lists](#task-lists)
- [Alerts and admonitions](#alerts-and-admonitions)
- [Footnotes](#footnotes)
- [Definition lists](#definition-lists)
- [Emoji](#emoji)
- [Escaping characters](#escaping-characters)
- [Reference-style links and images](#reference-style-links-and-images)
- [Extended code blocks](#extended-code-blocks)
- [HTML in Markdown](#html-in-markdown)
- [GitHub Flavored Markdown](#github-flavored-markdown)
- [Putting it together: Technical specification](#putting-it-together-technical-specification)
- [Practice exercises](#practice-exercises)
- [Summary](#summary)
- [Next steps](#next-steps)

---

## Introduction

Part 2 builds on the basics to teach extended Markdown syntax. These features are widely supported across platforms like GitHub, GitLab, and most documentation generators.

### What you'll learn

- Creating and formatting tables
- Task lists for tracking progress
- Alerts for highlighting important information
- Footnotes for references
- Emoji shortcodes
- Escaping special characters
- GitHub Flavored Markdown (GFM) specifics

### Prerequisites

- Completion of [Part 1: Markdown Basics](./series-part1-basics.md)
- Familiarity with basic Markdown syntax

[↑ Back to Table of Contents](#table-of-contents)

---

## Tables

Tables are essential for presenting structured data.

### Basic syntax

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

**Result:**

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |

### Column alignment

Control text alignment with colons in the separator row:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
| L2   | C2     | R2    |
```

**Result:**

| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
| L2   | C2     | R2    |

**Alignment syntax:**
- `:---` Left align (default)
- `:---:` Center align
- `---:` Right align

### Tables with formatting

You can use formatting inside cells:

```markdown
| Feature | Status | Notes |
|---------|--------|-------|
| **Login** | :white_check_mark: Done | `auth.js` |
| *Registration* | :construction: WIP | Needs review |
| ~~Legacy API~~ | :x: Deprecated | Remove in v2 |
```

**Result:**

| Feature | Status | Notes |
|---------|--------|-------|
| **Login** | :white_check_mark: Done | `auth.js` |
| *Registration* | :construction: WIP | Needs review |
| ~~Legacy API~~ | :x: Deprecated | Remove in v2 |

### Escaping pipes in tables

Use `\|` to include a literal pipe:

```markdown
| Expression | Result |
|------------|--------|
| `a \| b`   | OR     |
```

### Multi-line cells

Standard Markdown doesn't support multi-line cells. Use `<br>` for line breaks:

```markdown
| Step | Description |
|------|-------------|
| 1 | First action<br>Additional detail |
| 2 | Second action |
```

### Best practices

1. **Align columns** in source for readability (optional but helpful)
2. **Keep tables simple** - complex tables are hard to maintain
3. **Use alignment** purposefully (numbers right, text left)
4. **Consider alternatives** for complex data (code blocks, lists)

```markdown
# Bad: Inconsistent spacing
|Header|Another|
|---|---|
|data|more|

# Good: Aligned and readable
| Header  | Another |
|---------|---------|
| data    | more    |
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Task lists

Task lists (checkboxes) are perfect for tracking progress.

### Basic syntax

```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another pending task
```

**Result:**

- [x] Completed task
- [ ] Incomplete task
- [ ] Another pending task

### Nested task lists

```markdown
- [ ] Main task
  - [x] Subtask 1
  - [ ] Subtask 2
  - [ ] Subtask 3
- [x] Another main task
```

**Result:**

- [ ] Main task
  - [x] Subtask 1
  - [ ] Subtask 2
  - [ ] Subtask 3
- [x] Another main task

### Interactive checkboxes

On platforms like GitHub, checkboxes in issues and pull requests are **interactive** - you can click them to toggle state.

### Use cases

```markdown
## Release checklist

- [x] Code complete
- [x] Tests passing
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] Version bumped
- [ ] Tagged for release

## PR review

- [ ] Code follows style guide
- [ ] Tests included
- [ ] No security issues
- [ ] Performance considered
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Alerts and admonitions

Alerts (also called admonitions or callouts) highlight important information.

### GitHub-style alerts

GitHub Flavored Markdown supports these alert types:

```markdown
> [!NOTE]
> Useful information that users should know, even when skimming.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.
```

**Results:**

> [!NOTE]
> Useful information that users should know, even when skimming.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.

### Multi-line alerts

```markdown
> [!WARNING]
> This is a warning that spans multiple lines.
>
> You can include:
> - Lists
> - **Formatting**
> - `Code`
```

### When to use each type

| Alert Type | Use For |
|------------|---------|
| NOTE | Supplementary information, tips |
| TIP | Suggestions, shortcuts, best practices |
| IMPORTANT | Critical information for success |
| WARNING | Potential problems, gotchas |
| CAUTION | Actions that could cause harm or data loss |

### Platform variations

Different platforms have different syntax:

```markdown
<!-- GitHub/GitLab -->
> [!NOTE]
> Content

<!-- MkDocs (with admonition extension) -->
!!! note
    Content

<!-- Docusaurus -->
:::note
Content
:::
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Footnotes

Footnotes add references without interrupting the flow of text.

### Basic syntax

```markdown
Here's a statement that needs a citation.[^1]

[^1]: This is the footnote content.
```

**Result:**

Here's a statement that needs a citation.[^1]

[^1]: This is the footnote content.

### Named footnotes

Use descriptive names instead of numbers:

```markdown
Markdown was created by John Gruber.[^gruber]

[^gruber]: John Gruber introduced Markdown in 2004 on his blog Daring Fireball.
```

### Multi-line footnotes

Indent continuation lines:

```markdown
Here's a longer reference.[^long]

[^long]: This footnote has multiple paragraphs.

    Indent paragraphs to include them in the footnote.

    You can also include code blocks:

        code here
```

### Multiple references

Reference the same footnote multiple times:

```markdown
First reference[^note] and second reference[^note].

[^note]: This footnote is referenced twice.
```

### Best practices

1. **Use sparingly** - too many footnotes disrupt reading
2. **Keep footnotes concise** - they're for brief notes, not essays
3. **Place definitions at the end** of the document
4. **Use descriptive names** when the reference meaning matters

[↑ Back to Table of Contents](#table-of-contents)

---

## Definition lists

Definition lists display terms with their definitions. Support varies by platform.

### Syntax

```markdown
Term 1
: Definition for term 1

Term 2
: Definition for term 2
: Additional definition for term 2
```

**Result (where supported):**

Term 1
: Definition for term 1

Term 2
: Definition for term 2
: Additional definition for term 2

### Alternative using bold

For broader compatibility:

```markdown
**Term 1**: Definition for term 1

**Term 2**: Definition for term 2
```

### Alternative using tables

```markdown
| Term | Definition |
|------|------------|
| API | Application Programming Interface |
| REST | Representational State Transfer |
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Emoji

Emoji add visual interest and convey tone.

### Shortcodes

GitHub and many platforms support emoji shortcodes:

```markdown
:smile: :rocket: :warning: :+1: :-1:
```

**Result:** :smile: :rocket: :warning: :+1: :-1:

### Common emoji for documentation

| Category | Emoji | Shortcode | Use For |
|----------|-------|-----------|---------|
| Status | :white_check_mark: | `:white_check_mark:` | Complete/success |
| Status | :x: | `:x:` | Failed/error |
| Status | :warning: | `:warning:` | Warning |
| Status | :construction: | `:construction:` | Work in progress |
| Action | :rocket: | `:rocket:` | Launch/deploy |
| Action | :bug: | `:bug:` | Bug/issue |
| Action | :memo: | `:memo:` | Documentation |
| Action | :bulb: | `:bulb:` | Idea/tip |
| Info | :information_source: | `:information_source:` | Information |
| Info | :question: | `:question:` | Question |

### Unicode emoji

You can also paste emoji directly:

```markdown
Launch 🚀 | Success ✅ | Warning ⚠️
```

### Best practices

1. **Use sparingly** in technical documentation
2. **Be consistent** with emoji choices
3. **Consider accessibility** - screen readers may read emoji names
4. **Prefer shortcodes** for consistency across platforms

> [!NOTE]
> Emoji shortcode support varies by platform. GitHub, GitLab, and Slack support them. Standard Markdown renderers may not.

[↑ Back to Table of Contents](#table-of-contents)

---

## Escaping characters

Sometimes you need to display Markdown syntax characters literally.

### Backslash escapes

Use backslash (`\`) before special characters:

```markdown
\*Not italic\*
\# Not a heading
\[Not a link\]
\`Not code\`
```

**Result:**

\*Not italic\*
\# Not a heading

### Characters that can be escaped

```text
\   backslash
`   backtick
*   asterisk
_   underscore
{}  curly braces
[]  square brackets
()  parentheses
#   hash
+   plus sign
-   minus sign
.   dot
!   exclamation mark
|   pipe (in tables)
```

### Common escaping scenarios

```markdown
<!-- Showing literal asterisks -->
Use \*\*bold\*\* for bold text.

<!-- Showing literal backticks -->
Use \`code\` for inline code.

<!-- Showing literal brackets -->
This is not a link: \[text\](url)

<!-- In file paths -->
C:\\Users\\Name\\Documents
```

### Backticks in code

Use more backticks than the content contains:

```markdown
`` `single` ``     → `single`
``` `` double `` ```  → `` double ``
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Reference-style links and images

Reference-style syntax separates URLs from text for cleaner documents.

### Reference links

```markdown
Check out [Markdown Guide][mdguide] and [CommonMark][cm] for specifications.

Read more in the [Markdown Guide][mdguide] getting started section.

[mdguide]: https://www.markdownguide.org "Markdown Guide"
[cm]: https://commonmark.org
```

### Benefits

1. **Cleaner text** - URLs don't interrupt reading
2. **Reusability** - use the same link multiple times
3. **Easy maintenance** - update URL in one place
4. **Readability** - source text reads like natural prose

### Reference images

```markdown
Our logo: ![Company Logo][logo]

See the architecture in ![System Diagram][arch].

[logo]: /images/logo.png "Company Logo"
[arch]: /images/architecture.png "System Architecture"
```

### Implicit link names

If the link text matches the reference, you can omit it:

```markdown
Check out [Markdown Guide][] for more.

[Markdown Guide]: https://www.markdownguide.org
```

### Organizing references

Place references at the end of the document or after each section:

```markdown
## Introduction

Learn about [Markdown][1] and [Git][2].

[1]: https://daringfireball.net/projects/markdown/
[2]: https://git-scm.com/

## Next Section
...
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Extended code blocks

### Diff highlighting

Show additions and removals:

````markdown
```diff
- const oldValue = 'deprecated';
+ const newValue = 'current';
  const unchanged = 'same';
```
````

**Result:**

```diff
- const oldValue = 'deprecated';
+ const newValue = 'current';
  const unchanged = 'same';
```

### Highlighting specific lines

Some platforms support line highlighting:

````markdown
```python {2,4-6}
def example():
    important = True  # highlighted
    normal = False
    also = "highlighted"  # highlighted
    these = "too"         # highlighted
    lines = "yes"         # highlighted
```
````

### Showing file names

Add a title to code blocks:

````markdown
```python title="config.py"
DATABASE_URL = "postgresql://localhost/mydb"
```
````

### Console output

Use `text` or `console` for command output:

````markdown
```console
$ npm install
added 150 packages in 3.2s

$ npm test
All tests passed!
```
````

### Language variations

```markdown
# JavaScript variants
```javascript
```js
```jsx
```typescript
```ts
```tsx

# Shell variants
```bash
```shell
```sh
```zsh
```console

# Config files
```json
```yaml
```toml
```ini
```xml
```

[↑ Back to Table of Contents](#table-of-contents)

---

## HTML in Markdown

Most Markdown parsers accept raw HTML.

### Common HTML in Markdown

```markdown
<!-- Comments (invisible in output) -->

<br> <!-- Line break -->

<sub>subscript</sub> and <sup>superscript</sup>

<details>
<summary>Click to expand</summary>

Hidden content here.

</details>

<kbd>Ctrl</kbd> + <kbd>C</kbd>  <!-- Keyboard keys -->
```

**Results:**

<sub>subscript</sub> and <sup>superscript</sup>

<details>
<summary>Click to expand</summary>

Hidden content here.

</details>

<kbd>Ctrl</kbd> + <kbd>C</kbd>

### Collapsible sections

```markdown
<details>
<summary>Click for solution</summary>

```python
def solution():
    return 42
```

</details>
```

### HTML tables for complex layouts

When Markdown tables aren't enough:

```markdown
<table>
  <tr>
    <th>Header 1</th>
    <th colspan="2">Header 2 (spans 2 columns)</th>
  </tr>
  <tr>
    <td rowspan="2">Row 1-2</td>
    <td>Cell 1</td>
    <td>Cell 2</td>
  </tr>
  <tr>
    <td>Cell 3</td>
    <td>Cell 4</td>
  </tr>
</table>
```

### Best practices

1. **Use HTML sparingly** - defeats Markdown's simplicity
2. **Prefer Markdown** when possible
3. **Test compatibility** - some platforms restrict HTML
4. **Add blank lines** around HTML blocks

> [!WARNING]
> Some platforms (like GitHub README files) filter certain HTML tags for security.

[↑ Back to Table of Contents](#table-of-contents)

---

## GitHub Flavored Markdown

GitHub Flavored Markdown (GFM) extends CommonMark with additional features.

### GFM-specific features

| Feature | Standard Markdown | GFM |
|---------|-------------------|-----|
| Tables | No | Yes |
| Task lists | No | Yes |
| Strikethrough | No | Yes (`~~text~~`) |
| Autolinks | Limited | Extended |
| Alerts | No | Yes |
| Emoji shortcodes | No | Yes |

### Autolinks in GFM

GFM automatically links:

```markdown
<!-- URLs -->
Visit https://github.com for more.

<!-- Mentions -->
Thanks to @username for the contribution.

<!-- Issues/PRs -->
This fixes #123 and relates to #456.

<!-- Commits -->
See commit abc1234 for details.
```

### Username mentions

```markdown
@username - Mentions a user
@org/team - Mentions a team
```

### Issue and PR references

```markdown
#123                    - Issue/PR in same repo
org/repo#123            - Issue/PR in different repo
https://github.com/...  - Full URL (auto-linked)
```

### Commit references

```markdown
abc1234                 - Short SHA in same repo
org/repo@abc1234        - SHA in different repo
```

### Keyboard keys

```markdown
Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>
```

**Result:** Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>

[↑ Back to Table of Contents](#table-of-contents)

---

## Putting it together: Technical specification

Here's a complete technical specification using intermediate features:

```markdown
# Feature specification: User authentication

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Status:** Draft

## Overview

This document describes the authentication system for the application.

## Requirements

| ID | Requirement | Priority | Status |
|:---|:------------|:--------:|:------:|
| R1 | Support email/password login | High | :white_check_mark: |
| R2 | Support OAuth providers | High | :construction: |
| R3 | Implement MFA | Medium | :x: |
| R4 | Session management | High | :white_check_mark: |

## Implementation checklist

- [x] Database schema design
- [x] Password hashing implementation
- [ ] OAuth integration
  - [x] Google
  - [ ] GitHub
  - [ ] Microsoft
- [ ] MFA support
- [ ] Rate limiting

## Technical details

### Authentication flow

> [!IMPORTANT]
> All passwords must be hashed using bcrypt with a cost factor of 12.

The authentication flow works as follows[^flow]:

1. User submits credentials
2. Server validates against database
3. On success, JWT token is issued
4. Token is stored in HTTP-only cookie

[^flow]: See RFC 7519 for JWT specification details.

### Code example

```typescript
interface AuthResult {
  success: boolean;
  token?: string;
  error?: string;
}

async function authenticate(
  email: string,
  password: string
): Promise<AuthResult> {
  // Implementation
}
```

### API endpoints

| Endpoint | Method | Description |
|:---------|:------:|:------------|
| `/auth/login` | POST | User login |
| `/auth/logout` | POST | User logout |
| `/auth/refresh` | POST | Refresh token |
| `/auth/verify` | GET | Verify token |

> [!WARNING]
> Never store plain-text passwords. Always use proper hashing.

## See also

- [Security Guidelines][security]
- [API Documentation][api]

[security]: ./security.md
[api]: ./api.md
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Practice exercises

### Exercise 1: Tables

Create a comparison table with:
- At least 4 columns
- Different alignments (left, center, right)
- At least 5 rows of data
- Some cells with formatting (bold, code)

### Exercise 2: Task lists

Create a project checklist with:
- At least 3 main tasks
- Nested subtasks
- Mix of completed and pending items

### Exercise 3: Alerts

Write documentation that uses:
- A NOTE for additional information
- A WARNING for a common mistake
- A TIP for a best practice

### Exercise 4: Complete specification

Create a mini specification document with:
- Tables for requirements
- Task lists for implementation status
- Footnotes for references
- Code examples
- Appropriate alerts

[↑ Back to Table of Contents](#table-of-contents)

---

## Summary

In Part 2, you learned:

| Feature | Syntax |
|---------|--------|
| Tables | Pipe-separated with headers |
| Task lists | `- [x]` and `- [ ]` |
| Alerts | `> [!TYPE]` |
| Footnotes | `[^1]` and `[^1]:` |
| Emoji | `:shortcode:` |
| Escaping | `\*` |
| Reference links | `[text][ref]` |
| Diff code | ` ```diff ` |
| HTML | `<details>`, `<kbd>`, etc. |

### Key principles

1. **Know your platform** - not all features work everywhere
2. **Tables for data** - use them for structured information
3. **Alerts for emphasis** - don't overuse them
4. **Reference style for complex docs** - keeps text readable

[↑ Back to Table of Contents](#table-of-contents)

---

## Next steps

Continue to **[Part 3: Advanced techniques](./series-part3-advanced.md)** to learn:

- Mermaid diagrams (flowcharts, sequence diagrams, etc.)
- Mathematical equations with LaTeX/KaTeX
- Document conversion with Pandoc
- Static site generators and documentation frameworks
- Linting and automation
- Advanced workflows

---

[↑ Back to Table of Contents](#table-of-contents)
