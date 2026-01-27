# Validation report: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 26, 2026
> **Maintainers:** GDS Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Validation-blue)

> [!IMPORTANT]
> **Scope:** Validation of `dbtool-cli` design specifications against industry best practices (AWS CLI, Azure CLI, gcloud CLI) and documentation standards.

## Table of contents

- [Executive summary](#executive-summary)
- [Documentation standards compliance](#documentation-standards-compliance)
- [CLI design validation](#cli-design-validation)
  - [Architecture and frameworks](#architecture-and-frameworks)
  - [Command structure](#command-structure)
  - [Output and formatting](#output-and-formatting)
  - [Configuration management](#configuration-management)
  - [Error handling](#error-handling)
  - [Cross-platform compatibility](#cross-platform-compatibility)
- [Comparison with major CLIs](#comparison-with-major-clis)
  - [AWS CLI patterns](#aws-cli-patterns)
  - [Azure CLI patterns](#azure-cli-patterns)
  - [gcloud CLI patterns](#gcloud-cli-patterns)
- [Gap analysis](#gap-analysis)
- [Recommendations](#recommendations)
- [Review checklist](#review-checklist)

## Executive summary

The `dbtool-cli` project is in the **Initiation/Design** phase. The existing documentation outlines a robust, modern Python-based CLI using Typer and Rich frameworks.

### Overall assessment

| Category | Score | Notes |
|:---|:---:|:---|
| Documentation Standards | 95% | Formatting issues fixed, acronyms defined |
| CLI Design | 95% | Enterprise features added (dry-run, env vars, progress) |
| Best Practices Alignment | 90% | Aligned with AWS/Azure/gcloud patterns |

**Verdict:** The design now aligns with modern CLI best practices. Critical gaps (dry-run, progress indicators, environment variables) have been addressed. Remaining items (YAML output, shell completion docs) are nice-to-have enhancements.

[↑ Back to Table of Contents](#table-of-contents)

## Documentation standards compliance

Validation against `docs/best-practices/documentation-standards.md`.

### Structure and organization

| Requirement | Status | Notes |
|:---|:---:|:---|
| Diátaxis folder placement | ⚠️ | Project docs in `projects/` rather than standard Diátaxis folders |
| Descriptive H1 titles | ✅ | All documents have clear titles |
| Metadata header (Version, Date, Maintainer, Status) | ✅ | Present in all documents |
| Navigation links (Back to Index) | ✅ | Consistent across all documents |
| Table of Contents | ✅ | Present in all documents |
| "Back to TOC" links after major sections | ✅ | Implemented consistently |

### Content quality

| Requirement | Status | Notes |
|:---|:---:|:---|
| Sentence-case headings | ✅ | Correctly implemented |
| Code blocks with language tags | ✅ | All code blocks properly tagged |
| Active voice, present tense | ✅ | Writing style is appropriate |
| Acronyms defined on first use | ⚠️ | Some acronyms (DBRE, MTTR) not defined |
| US English spelling | ✅ | Consistent |

### Issues found

1. **functional-spec.md:18-19** - Duplicate TOC entry: `[Interfaces & commands](#3-interfaces--commands)` appears twice
2. **technical-architecture.md:20-21** - Duplicate TOC entry: `[Configuration schema](#6-configuration-schema)` appears twice
3. **technical-architecture.md:166-167** - Duplicate "Back to TOC" link
4. **validation_report.md** - File uses underscore (`validation_report.md`) instead of kebab-case (`validation-report.md`)
5. **troubleshooting.md:183** - Inconsistent flag reference: uses `--verbose` but global args define `--debug`
6. **Missing acronym definitions**: DBRE, MTTR, AD, SPN, TTL, NFR, ADR should be defined on first use

[↑ Back to Table of Contents](#table-of-contents)

## CLI design validation

### Architecture and frameworks

| Feature | dbtool Design | Best Practice | Status |
|:---|:---|:---|:---:|
| Framework | Typer + Rich | Modern standard for Python CLIs | ✅ |
| Type hints | Python 3.12+ with type annotations | Enables auto-completion and validation | ✅ |
| Output library | Rich (tables, spinners, colors) | Industry standard for terminal UI | ✅ |
| Auth abstraction | Platform-aware (Kerberos/AD) | Respects OS-native patterns | ✅ |
| Config format | TOML | Human-readable, standard format | ✅ |

**Assessment:** Framework choices align with [Typer best practices](https://typer.tiangolo.com/) and industry standards.

[↑ Back to Table of Contents](#table-of-contents)

### Command structure

Comparison with [CLI Guidelines](https://clig.dev/) and major cloud CLIs.

| Pattern | dbtool Design | Best Practice | Status |
|:---|:---|:---|:---:|
| Verb-noun consistency | Mixed (`dbtool sql`, `dbtool vault list`) | Consistent ordering | ⚠️ |
| Short aliases | Yes (`ck`, `sh`, `lb`, `tf`, `vt`) | Standard short forms available | ✅ |
| Help flag | `--help` | Both `-h` and `--help` | ⚠️ |
| Global flags | `--debug`, `--profile`, `--help` | Standard set documented | ✅ |
| Subcommand depth | 2 levels max | Avoid excessive nesting | ✅ |

**Command structure analysis:**

```text
dbtool <command> [subcommand] [arguments] [options]

Examples:
  dbtool check <target>           # verb-first
  dbtool vault list [path]        # noun-verb (like gcloud)
  dbtool sql <target> "<query>"   # verb + positional args
```

**Issues identified:**

1. **Inconsistent verb-noun ordering**: `dbtool sql` (verb) vs `dbtool vault list` (noun-verb)
2. **Missing `-h` short form**: Only `--help` documented
3. **Missing `--version` in command reference**: Standard flag not documented
4. **Positional argument overload**: `dbtool sql <target> "<query>"` mixes target and query as positional args

[↑ Back to Table of Contents](#table-of-contents)

### Output and formatting

| Feature | dbtool Design | Best Practice | Status |
|:---|:---|:---|:---:|
| Human-readable default | Table format | ✅ Human-first | ✅ |
| Machine-readable option | `--format json` | ✅ Scripting support | ✅ |
| CSV support | `--format csv` | Data export capability | ✅ |
| Progress indicators | Not documented | Required for long operations | ❌ |
| Color handling | Not documented | Support `NO_COLOR`, `--no-color` | ❌ |
| Pager support | Not documented | Use `less` for long output | ❌ |

**Missing output features:**

1. No `--quiet` / `-q` flag for minimal output
2. No `--no-color` flag or `NO_COLOR` environment variable support
3. No progress bar/spinner specification for long-running commands
4. No pager integration for lengthy output

[↑ Back to Table of Contents](#table-of-contents)

### Configuration management

| Feature | dbtool Design | Best Practice (AWS/gcloud) | Status |
|:---|:---|:---|:---:|
| Config file location | XDG/AppData paths | ✅ Platform-appropriate | ✅ |
| Named profiles | `[profile.default]`, `[profile.prod]` | ✅ Environment switching | ✅ |
| Profile switching | `dbtool config use <profile>` | ✅ Runtime selection | ✅ |
| Environment variables | Not documented | Override config values | ❌ |
| Config precedence | CLI > Env > Config (ADR-004) | ✅ Standard order | ✅ |

**Configuration precedence (documented in ADR-004):**
1. CLI flags (highest)
2. Environment variables
3. Config file (lowest)

**Missing configuration features:**

1. **Environment variable naming convention not defined**: Should document `DBTOOL_*` prefix
2. **No `.env` file support**: Common for project-specific overrides
3. **No `dbtool config init` command**: Would help new users bootstrap configuration

[↑ Back to Table of Contents](#table-of-contents)

### Error handling

| Feature | dbtool Design | Best Practice | Status |
|:---|:---|:---|:---:|
| Exit codes | Documented (0-6) | ✅ Standard codes | ✅ |
| Error messages | Named constants (VAULT_AUTH_FAILED) | ✅ Consistent format | ✅ |
| Actionable guidance | Resolution steps provided | ✅ User-friendly | ✅ |
| Debug output | `--debug` flag | ✅ Troubleshooting support | ✅ |
| Log files | Documented locations | ✅ Post-mortem analysis | ✅ |

**Assessment:** Error handling design is comprehensive and follows best practices.

[↑ Back to Table of Contents](#table-of-contents)

### Cross-platform compatibility

| Component | Windows | Linux | Status |
|:---|:---|:---|:---:|
| Path handling | `pathlib` | `pathlib` | ✅ |
| Authentication | AD/LDAP prompt | Kerberos auto | ✅ |
| Config location | `%APPDATA%\dbtool\` | `~/.config/dbtool/` | ✅ |
| Log location | `%APPDATA%\dbtool\logs\` | `~/.local/state/dbtool/logs/` | ✅ |
| Distribution | PyInstaller EXE | PEX/Shiv binary | ✅ |

**Assessment:** Cross-platform strategy is well-designed and addresses "Two Worlds" problem effectively.

[↑ Back to Table of Contents](#table-of-contents)

## Comparison with major CLIs

### AWS CLI patterns

Reference: [AWS CLI Command Structure](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-commandstructure.html)

| Pattern | AWS CLI | dbtool | Gap |
|:---|:---|:---|:---|
| Command structure | `aws <service> <action>` | `dbtool <command> [subcommand]` | Similar ✅ |
| Named profiles | `--profile <name>` | `--profile <name>` | Aligned ✅ |
| Output formats | `--output json\|text\|table\|yaml` | `--format json\|csv\|table` | Missing YAML |
| Query/filter | `--query <JMESPath>` | Not supported | Missing |
| Wait commands | `aws <service> wait <condition>` | Not applicable | N/A |
| Auto-prompt | `aws --cli-auto-prompt` | Not documented | Missing |
| Dry-run | `--dry-run` on destructive ops | Not documented | Missing |

**Key AWS CLI features to consider:**

1. **JMESPath querying**: `--query` flag for filtering JSON output
2. **Auto-prompt mode**: Interactive command building
3. **Dry-run support**: Preview destructive operations
4. **YAML output**: Additional format option

[↑ Back to Table of Contents](#table-of-contents)

### Azure CLI patterns

Reference: [Azure CLI Design](https://azure.github.io/azure-sdk/python_design.html)

| Pattern | Azure CLI | dbtool | Gap |
|:---|:---|:---|:---|
| Command structure | `az <group> <subgroup> <action>` | `dbtool <command> [subcommand]` | Similar ✅ |
| Output formats | `--output json\|jsonc\|yaml\|table\|tsv` | `--format json\|csv\|table` | Missing YAML, TSV |
| Query support | `--query <JMESPath>` | Not supported | Missing |
| Verbose/debug | `--verbose`, `--debug` | `--debug` | Missing `--verbose` |
| Subscription context | `az account set` | `dbtool config use` | Aligned ✅ |
| Interactive mode | `az interactive` | Not planned | Consider for v2 |

**Key Azure CLI features to consider:**

1. **Colorized JSON (jsonc)**: Syntax-highlighted JSON output
2. **TSV output**: Tab-separated for shell processing
3. **Verbose vs Debug**: Two levels of output detail

[↑ Back to Table of Contents](#table-of-contents)

### gcloud CLI patterns

Reference: [gcloud CLI Overview](https://cloud.google.com/sdk/gcloud)

| Pattern | gcloud CLI | dbtool | Gap |
|:---|:---|:---|:---|
| Command structure | `gcloud <component> <entity> <action>` | `dbtool <command> [subcommand]` | Similar ✅ |
| Release levels | `alpha`, `beta`, GA | Not applicable | N/A |
| Configurations | `gcloud config configurations` | `dbtool config profiles` | Aligned ✅ |
| Output formats | `--format=json\|yaml\|csv\|table` | `--format json\|csv\|table` | Missing YAML |
| Filtering | `--filter=<expression>` | Not supported | Missing |
| Quiet mode | `--quiet` | Not documented | Missing |
| Impersonation | `--impersonate-service-account` | Not applicable | N/A |

**Key gcloud CLI features to consider:**

1. **Filter expressions**: Client-side result filtering
2. **Quiet mode**: Suppress prompts and reduce output
3. **Format customization**: Rich format string support

[↑ Back to Table of Contents](#table-of-contents)

## Gap analysis

### Critical gaps (P0) - RESOLVED

| Gap | Status | Resolution |
|:---|:---:|:---|
| No `--dry-run` for destructive operations | ✅ Fixed | Added `--dry-run` to `vault delete`, `vault put`, `lb update`, `lb rollback`, `tf apply` in command-reference.md |
| No progress indicators documented | ✅ Fixed | Added section 8 "Progress indicators" in technical-architecture.md |
| Environment variables not documented | ✅ Fixed | Added "Environment variables" section in command-reference.md and section 7 in technical-architecture.md |

### Important gaps (P1) - PARTIALLY RESOLVED

| Gap | Status | Resolution |
|:---|:---:|:---|
| No `-h` short form for help | ✅ Fixed | Added `-h` alias in command-reference.md global arguments |
| No `--quiet` flag | ✅ Fixed | Added `-q`/`--quiet` in command-reference.md and NFR-08 |
| No `--no-color` flag | ✅ Fixed | Added `--no-color` and `NO_COLOR` in command-reference.md and NFR-04 |
| No YAML output format | ⚠️ Open | Consider adding `--format yaml` in future version |
| Inconsistent verb-noun ordering | ⚠️ Open | Recommend standardizing on noun-verb pattern |

### Nice-to-have gaps (P2)

| Gap | Impact | Recommendation |
|:---|:---|:---|
| No query/filter support | Power user friction | Consider `--query` with JMESPath |
| No shell completion docs | Discoverability | Document Typer's built-in completion |
| No plugin architecture | Extensibility | Consider `dbtool-<plugin>` executable pattern |
| No interactive mode | Onboarding experience | Consider for v2 |

[↑ Back to Table of Contents](#table-of-contents)

## Recommendations

### Immediate actions (before implementation) - COMPLETED

1. **Fix documentation issues** ✅
   - ~~Remove duplicate TOC entries in functional-spec.md and technical-architecture.md~~
   - ~~Rename `validation_report.md` to `validation-report.md`~~
   - ~~Define acronyms on first use (DBRE, MTTR, AD, SPN, TTL)~~
   - ~~Align verbose flag naming (`--debug` vs `--verbose`)~~

2. **Update command reference** ✅
   - ~~Add `-h` as alias for `--help`~~
   - ~~Add `--version` / `-V` flag~~
   - ~~Add `--quiet` / `-q` flag~~
   - ~~Add `--no-color` flag~~
   - ~~Document `--dry-run` for destructive operations~~

3. **Document environment variables** ✅
   - ~~Added to command-reference.md and technical-architecture.md~~

### Short-term improvements (MVP)

1. **Standardize command structure** (Open)
   - Choose either verb-noun or noun-verb consistently
   - Recommended: noun-verb like gcloud (`dbtool db check`, `dbtool vault list`)

2. **Add progress indicators** ✅
   - ~~Documented in technical-architecture.md section 8~~

3. **Add output format options** (Open)
   - Add YAML format: `--format yaml`
   - Consider TSV for shell processing: `--format tsv`

### Long-term enhancements (v2)

1. **Query/filter support**
   - Add `--query` flag with JMESPath expressions
   - Add `--filter` for client-side filtering

2. **Plugin architecture**
   - Support `dbtool-<name>` executables in PATH
   - Document plugin development guide

3. **Interactive mode**
   - Consider `dbtool interactive` for guided command building

[↑ Back to Table of Contents](#table-of-contents)

## Review checklist

### Documentation completeness

- [x] README with project overview
- [x] Functional specification with user stories
- [x] Command reference with all commands
- [x] Technical architecture with diagrams
- [x] Decision log (ADRs)
- [x] Troubleshooting guide
- [ ] Installation guide (missing)
- [ ] Contributing guide (missing)
- [ ] Changelog (missing)

### CLI design completeness

- [x] Command structure defined
- [x] Authentication flows documented
- [x] Error codes and messages defined
- [x] Configuration schema documented
- [x] Environment variables documented
- [ ] Shell completion documented
- [x] Progress indicator behavior documented
- [x] Color/accessibility options documented

### Best practices alignment

- [x] Human-readable default output
- [x] Machine-readable option (JSON)
- [x] Named profiles for environment switching
- [x] Platform-appropriate config locations
- [x] Comprehensive error handling
- [x] Dry-run for destructive operations
- [x] Quiet mode for scripting
- [x] Standard flag aliases (-h, -q)

[↑ Back to Table of Contents](#table-of-contents)

---

## Sources

- [Command Line Interface Guidelines (clig.dev)](https://clig.dev/)
- [AWS CLI Command Structure](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-commandstructure.html)
- [Azure CLI Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Azure CLI Python Success Story](https://www.python.org/success-stories/building-an-open-source-and-cross-platform-azure-cli-with-python/)
- [gcloud CLI Overview](https://cloud.google.com/sdk/gcloud)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Typer CLI Best Practices](https://www.projectrules.ai/rules/typer)
- [AWS SAM CLI Design](https://github.com/aws/aws-sam-cli/blob/develop/DESIGN.md)
