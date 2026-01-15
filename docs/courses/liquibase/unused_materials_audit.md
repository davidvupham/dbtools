# Audit of Unused Files in Liquibase Course Part 1 & 2

The following is a list of **files, scripts, and artifacts** found within the `docs/courses/liquibase` directory structure that are **NOT** explicitly referenced in either `series-part1-baseline.md` or `series-part2-manual.md`.

These items likely belong to Part 3 (CI/CD), internal testing/validation tools, or documentation standards.

## Root Directory (`docs/courses/liquibase/`)
*   `BEST_PRACTICES_MODULARITY.md`
*   `README.md`
*   `REFACTORING_SUMMARY.md`
*   `architecture.md`
*   `course_overview.md`
*   `glossary.md`
*   `liquibase_course_design.md`
*   `naming_conventions.md`
*   `quick_reference.md`
*   `troubleshooting.md`
*   `part3_validation_20260112_215039.log`

## Learning Paths (`docs/courses/liquibase/learning-paths/`)
*   `TUTORIAL_COMPARISON.md`
*   `tutorial-supplement-end-to-end-pipeline.md`

## Scripts (`docs/courses/liquibase/scripts/`)

### Documentation & Tests
*   `README.md`
*   `TEST_RESULTS_DYNAMIC_PORTS.md`
*   `manual_review_part2.md`
*   `review_tutorial_grammar.sh`

### Setup & Configuration
*   `build_container_image.sh` (Text instructs running `cr build` commands manually)
*   `configure_paths.sh`
*   `setup_environment.sh`
*   `setup_tutorial_port.sh`
*   `setup-github-runner-config.sh` (Part 3 related)

### Helpers (Indirectly Used)
*Some scripts are used via aliases (e.g., `lb`, `sqlcmd-tutorial`) but their actual filenames are not explicitly referenced in the markdown text.*
*   `lb.sh`
*   `sqlcmd_tutorial.sh`

### Testing & Validation (Internal/Part 3)
*   `container_diagnostic.sh`
*   `deploy_liquibase_baseline.sh` (Text uses `deploy.sh` or `generate_liquibase_baseline.sh`)
*   `test_block_ports.sh`
*   `test_dynamic_ports.sh`
*   `test_part2_steps.sh`
*   `test_port_discovery_integration.sh`
*   `test_tutorial_flow_dynamic_ports.sh`
*   `validate_part3_cicd.sh`
*   `validate_tutorial.sh`
*   `validate_tutorial_full.sh`
*   `validate_tutorial_part2.sh`
*   `verify-self-hosted-env.sh`

## SQL (`docs/courses/liquibase/sql/`)
*   `setup_orderdb_database.sql`

## Docker (`docs/courses/liquibase/docker/`)
*   `README.md`

## Validation (`docs/courses/liquibase/validation/`)
*   `ORGANIZATION_SUMMARY.md`
*   `README.md`
*   `reports/` (Directory)
