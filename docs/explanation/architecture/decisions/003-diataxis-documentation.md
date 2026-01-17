# ADR-003: Follow Diátaxis framework for documentation

## Status

Accepted

## Context

Technical documentation often becomes disorganized as projects grow, mixing tutorials with reference material and how-to guides with explanatory content. This makes it difficult for users to find what they need.

We evaluated several documentation frameworks:

1. **No framework**: Organize by feature or component
2. **ReadTheDocs structure**: Getting Started, User Guide, API Reference
3. **Diátaxis**: Four-quadrant system based on user needs
4. **Custom taxonomy**: Create our own categories

## Decision

We adopt the **Diátaxis framework** for organizing all documentation.

Documentation is organized into four categories:

| Category | Purpose | User Goal |
|----------|---------|-----------|
| **Tutorials** | Learning-oriented | "I want to learn..." |
| **How-to Guides** | Task-oriented | "I want to do..." |
| **Reference** | Information-oriented | "I want to know..." |
| **Explanation** | Understanding-oriented | "I want to understand..." |

Directory structure:
```
docs/
├── tutorials/      # Step-by-step learning experiences
├── how-to/         # Recipes for specific tasks
├── reference/      # API docs, configuration specs
└── explanation/    # Background, concepts, decisions
```

## Consequences

### Benefits

- **Clear organization**: Each document has an obvious home
- **User-focused**: Categories match what users are trying to accomplish
- **Scalable**: Works well as documentation grows
- **Industry recognition**: Widely adopted in technical writing

### Trade-offs

- **Requires discipline**: Writers must correctly categorize documents
- **Some overlap**: Some content could fit multiple categories
- **Migration effort**: Existing docs needed reorganization

### Guidelines

- **Tutorials**: Teach concepts through hands-on examples; assume minimal prior knowledge
- **How-to guides**: Assume user knows what they want; provide direct steps
- **Reference**: Complete, accurate, and consistently formatted
- **Explanation**: Discuss why, trade-offs, and alternatives

### Related standards

- File naming: kebab-case (e.g., `getting-started.md`)
- Headings: Sentence case (e.g., "Configure the database")
- See [Documentation Standards](../../../best-practices/documentation-standards.md) for full details
