# Liquibase Course - Claude Instructions

This file contains Claude Code instructions specific to the Liquibase tutorial course.

## Modifying Tutorials

When modifying tutorial content in `learning-paths/series-part*.md`, ensure the corresponding test scripts are updated to match.

After making changes to a tutorial or its scripts, run the test to verify everything works:

```bash
cd docs/courses/liquibase/scripts
./test_part1_baseline.sh    # Test Part 1 only
./test_part2_manual.sh      # Test Part 2 (runs Part 1 first, or use --skip-part1)
```

The test script executes the same scripts as the tutorial - it should not contain duplicate validation logic.

## Tutorial Validation (All Parts)

When validating any part of the Liquibase tutorial (`learning-paths/series-part*.md`):

1. **Execute step-by-step**: Run each command from the tutorial one at a time
2. **Show line numbers**: Reference which lines (e.g., "Lines 40-43") are being executed
3. **Display output**: Show full command output after each step
4. **Pause for approval**: Ask for user approval before proceeding to the next step

## Scripts Reference

Test scripts are in the `scripts/` directory:

| Tutorial | Test Script |
|----------|-------------|
| Part 1: `series-part1-baseline.md` | `scripts/test_part1_baseline.sh` |
| Part 2: `series-part2-manual.md` | `scripts/test_part2_manual.sh` (use `--skip-part1` if Part 1 already complete) |
| Part 3: `series-part3-cicd.md` | Manual validation required (GitHub interactions) |

## Quick Setup Reference (Part 3, Lines 39-82)

When recreating the Part 1 environment from Part 3's Quick Setup section:

| Lines | Description |
|-------|-------------|
| 40-43 | Configure environment and aliases |
| 46 | Clean up previous runs (optional) |
| 49 | Start SQL Server containers |
| 52-53 | Build Liquibase container |
| 56-58 | Verify SQL Server is running |
| 61 | Create project structure |
| 64-65 | Create and validate databases |
| 68-69 | Populate dev database |
| 72-73 | Configure Liquibase |
| 76-77 | Generate baseline |
| 80-81 | Deploy and validate baseline |
