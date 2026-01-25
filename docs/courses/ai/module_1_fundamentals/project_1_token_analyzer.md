# Project 1: Token Analyzer

**[← Back to Course Index](../README.md)**

> **Difficulty:** Beginner
> **Estimated Time:** 2-3 hours
> **Prerequisites:** Module 1 chapters completed

## Overview

Build a command-line tool that analyzes text tokenization, estimates costs, and helps users understand how LLMs process their input.

## Learning objectives

By completing this project, you will:

1. Implement tokenization using multiple tokenizer libraries
2. Calculate token counts and estimate API costs
3. Visualize how text is split into tokens
4. Handle edge cases in tokenization

## Requirements

### Functional requirements

1. **Token counting**: Count tokens using tiktoken (OpenAI) and SentencePiece (Llama)
2. **Cost estimation**: Calculate estimated API costs for different providers
3. **Token visualization**: Show how text is split into tokens with boundaries
4. **Context fit check**: Determine if text fits within common context windows
5. **Comparison mode**: Compare tokenization across different models

### Technical requirements

- Python 3.9+
- CLI interface using argparse or click
- Support for stdin, file input, and direct text input
- JSON output option for scripting

## Getting started

### Step 1: Set up the environment

```bash
# Create project directory
mkdir token-analyzer && cd token-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install tiktoken sentencepiece click rich
```

### Step 2: Create the basic structure

```python
# token_analyzer/analyzer.py
from dataclasses import dataclass


@dataclass
class TokenizationResult:
    text: str
    token_count: int
    tokens: list[str]
    tokenizer: str


class TokenAnalyzer:
    """Analyze text tokenization across different models."""

    def __init__(self):
        # Initialize tokenizers
        pass

    def tokenize(self, text: str, model: str = "gpt-4") -> TokenizationResult:
        """Tokenize text using specified model's tokenizer."""
        # Implement tokenization
        pass

    def estimate_cost(self, token_count: int, model: str) -> dict:
        """Estimate API cost for given token count."""
        # Implement cost calculation
        pass

    def check_context_fit(self, token_count: int) -> dict:
        """Check if text fits common context windows."""
        # Implement context checking
        pass
```

## Implementation guide

### Part 1: Token counting

Implement token counting for multiple models:

```python
import tiktoken


def count_tokens_openai(text: str, model: str = "gpt-4") -> int:
    """Count tokens using OpenAI's tokenizer."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

**Tasks:**
- [ ] Implement OpenAI tokenization (tiktoken)
- [ ] Implement Llama tokenization (SentencePiece)
- [ ] Handle tokenizer loading errors gracefully
- [ ] Add caching for tokenizer initialization

### Part 2: Cost estimation

Create a cost calculator:

```python
PRICING = {
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},  # per million tokens
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
}


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate cost in USD."""
    # Implement cost calculation
    pass
```

**Tasks:**
- [ ] Define pricing for major models
- [ ] Calculate input and output costs separately
- [ ] Support custom pricing configuration
- [ ] Format costs with appropriate precision

### Part 3: Token visualization

Show token boundaries visually:

```python
from rich.console import Console
from rich.text import Text


def visualize_tokens(text: str, tokens: list[str]) -> None:
    """Display text with token boundaries highlighted."""
    console = Console()
    # Use alternating colors to show token boundaries
    colors = ["green", "blue", "yellow", "magenta", "cyan"]
    # Implement visualization
    pass
```

**Tasks:**
- [ ] Highlight token boundaries with colors
- [ ] Show token IDs alongside text
- [ ] Handle special tokens (BOS, EOS, etc.)
- [ ] Support both terminal and plain text output

### Part 4: CLI interface

Create the command-line interface:

```python
import click


@click.group()
def cli():
    """Token Analyzer - Understand LLM tokenization."""
    pass


@cli.command()
@click.argument("text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True))
@click.option("--model", "-m", default="gpt-4")
@click.option("--json", "output_json", is_flag=True)
def count(text, file, model, output_json):
    """Count tokens in text."""
    # Implement command
    pass


@cli.command()
@click.argument("text", required=False)
@click.option("--model", "-m", default="gpt-4")
def visualize(text, model):
    """Visualize token boundaries."""
    # Implement command
    pass
```

## Expected output

### Token count

```bash
$ token-analyzer count "PostgreSQL is a powerful database" --model gpt-4
Model: gpt-4
Tokens: 6
Characters: 35
Ratio: 5.83 chars/token
```

### Cost estimation

```bash
$ token-analyzer cost --input 1000 --output 500 --model gpt-4-turbo
Model: gpt-4-turbo
Input tokens: 1,000 ($0.010)
Output tokens: 500 ($0.015)
Total: $0.025
```

### Visualization

```bash
$ token-analyzer visualize "PostgreSQL is a powerful database"
[Post][gres][QL][ is][ a][ powerful][ database]
  0    1     2    3    4      5         6
```

### Context check

```bash
$ token-analyzer check-context document.txt
Token count: 15,234

Context Window Compatibility:
✓ GPT-4 Turbo (128K)     - 11.9% used
✓ Claude 3 (200K)        - 7.6% used
✓ Llama 3.1 (128K)       - 11.9% used
✗ GPT-3.5 (16K)          - 95.2% used (WARNING: near limit)
```

## Stretch goals

1. **Web interface**: Add a simple Flask/FastAPI web UI
2. **Batch processing**: Process multiple files and generate reports
3. **Token diff**: Compare tokenization of similar texts
4. **Language detection**: Automatically detect language and adjust estimates

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| Token counting works for multiple models | 20 |
| Cost estimation is accurate | 20 |
| Visualization clearly shows boundaries | 20 |
| CLI is user-friendly and well-documented | 20 |
| Code quality and error handling | 20 |
| **Total** | **100** |

## Submission

Create a git repository with:
- Source code in `src/` or `token_analyzer/`
- README.md with installation and usage instructions
- Example outputs in `examples/`
- Tests in `tests/`

---

**[Next Module →](../module_2_prompt_engineering/06_prompt_anatomy.md)**
