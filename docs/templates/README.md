# Documentation Templates

**[← Back to Documentation Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)

Use these templates to create consistent, high-quality documentation that follows our [Documentation Standards](../best-practices/documentation-standards.md).

## Available Templates

| Template | Use Case | Diátaxis Type |
|:---|:---|:---|
| [tutorial-template.md](./tutorial-template.md) | Learning-oriented lessons for beginners | Tutorial |
| [how-to-template.md](./how-to-template.md) | Task-oriented recipes for specific goals | How-To |
| [reference-template.md](./reference-template.md) | API, configuration, and technical specs | Reference |
| [explanation-template.md](./explanation-template.md) | Conceptual background and architecture | Explanation |
| [adr-template.md](./adr-template.md) | Architecture Decision Records | Decision |

## How to Use

1. **Choose the right template** based on your documentation goal:
   - "I want to teach someone" → `tutorial-template.md`
   - "I want to show how to do X" → `how-to-template.md`
   - "I want to document facts" → `reference-template.md`
   - "I want to explain why" → `explanation-template.md`
   - "I want to record a decision" → `adr-template.md`

2. **Copy the template** to the appropriate directory:
   ```bash
   cp docs/templates/how-to-template.md docs/how-to/topic/my-guide.md
   ```

3. **Fill in the placeholders** (marked with `[brackets]`)

4. **Update metadata**:
   - Set the correct `Last Updated` date
   - Set your team as `Maintainers`
   - Change `Status` from `Draft` to `Production` when ready

5. **Remove unused sections** if they don't apply to your document

## Template Guidelines

### Placeholders

All templates use `[bracketed text]` for placeholders:
- `[Topic]` - Replace with your subject
- `[Month] [Day], [Year]` - Replace with current date
- `[Team Name]` - Replace with owning team

### Status Badges

Update the status badge to match your document status:

```markdown
![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Status](https://img.shields.io/badge/Status-Production-green)
![Status](https://img.shields.io/badge/Status-Deprecated-red)
```

### Navigation Links

Update the "Back to Index" link to point to the correct parent:

```markdown
**[← Back to How-To Index](../how-to/README.md)**
```

## Questions?

See the [Documentation Standards](../best-practices/documentation-standards.md) for complete guidelines on writing style, formatting, and review process.
