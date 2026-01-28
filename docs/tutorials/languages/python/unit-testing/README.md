# Python Unit Testing: Master Class
<!-- id: course-title -->

**[← Back to Python Tutorials Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** GDS Engineering Team
> **Status:** Production
> **Time Estimate:** 2-3 Hours

> [!NOTE]
> This course is designed to take you from "I write print statements" to "I architect robust, scalable test suites." We use standard industry patterns focusing on `pytest`.

## Table of Contents
<!-- id: toc -->
1.  [Getting Started](01-getting-started.md) - The AAA Pattern and your first test
2.  [Mastering Fixtures](02-fixtures.md) - Dependency injection and setup/teardown
3.  [Scaling with Parametrization](03-scaling-tests.md) - Writing one test to verify infinite inputs
4.  [The Art of Mocking](04-mocking.md) - Isolating dependencies effectively
5.  [Advanced Patterns](05-advanced-patterns.md) - Markers, Coverage, and CI/CD

## Course Overview
<!-- id: overview -->

Unit testing is not just about catching bugs; it is a design philosophy. Writing tests forces you to write modular, decoupled code. This course covers the "Golden Path" of Python testing using `pytest`, the industry-standard framework.

### You Will Learn
- **The Philosophy**: Why "Compose, Don't Inherit" applies to tests too.
- **The Tooling**: How to use `pytest` effectively (fixtures, markers, config).
- **The Patterns**: AAA (Arrange-Act-Assert) and Given-When-Then.
- **The Execution**: How to integrate tests into a modern standard workflow.

## Prerequisites
<!-- id: prereqs -->

- Basic understanding of Python syntax.
- `uv` installed (standard in this repo) or `pip`.
- A desire to stop debugging in production.

## Tutorial Resources
<!-- id: resources -->

All examples in this tutorial are available in the [examples](./examples/) directory. You can run them directly:

```bash
cd docs/tutorials/languages/python/unit-testing/examples
uv run pytest
```

## Getting Help
<!-- id: help -->

- [Official Pytest Documentation](https://docs.pytest.org/)
- [Better Specs](https://betterspecs.org/) (Structuring tests)
- Internal GDS Slack: `#dev-python`
