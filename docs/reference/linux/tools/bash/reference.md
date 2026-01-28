# Bash productivity reference

**[← Back to Linux Reference](../../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Bash-blue)

> [!TIP]
> These tricks work in both Bash and Zsh. Small workflow improvements add up to significant time savings.

## Table of contents

- [Directory navigation](#directory-navigation)
- [Command history](#command-history)
- [Brace expansion](#brace-expansion)
- [Command re-execution](#command-re-execution)
- [xargs](#xargs)
- [Aliases](#aliases)
- [less](#less)
- [Process substitution](#process-substitution)
- [tldr](#tldr)
- [Directory bookmarks with zoxide](#directory-bookmarks-with-zoxide)

## Directory navigation

### Jump to previous directory

Use `cd -` to switch back to your previous directory:

```bash
cd ~/projects/myapp
cd /etc/nginx
cd -
# Now you're back in ~/projects/myapp
```

[↑ Back to table of contents](#table-of-contents)

## Command history

### Search with Ctrl + R

Press `Ctrl + R` and type to search command history. Press `Ctrl + R` again to cycle through matches.

| Key | Action |
|:----|:-------|
| `Ctrl + R` | Start reverse search |
| `Ctrl + R` (again) | Next match |
| `Enter` | Execute command |
| `Ctrl + G` | Cancel search |

[↑ Back to table of contents](#table-of-contents)

## Brace expansion

Generate multiple files or directories with a single command:

```bash
# Create numbered files
touch file_{1..10}.txt

# Create multiple directories
mkdir project/{api,frontend,docs}

# Backup a file
cp config.{yml,yml.bak}

# Create nested structure
mkdir -p project/{src,tests}/{main,utils}
```

[↑ Back to table of contents](#table-of-contents)

## Command re-execution

### Re-run last command

```bash
!!
```

### Re-run last command with sudo

```bash
sudo !!
```

### Use last argument from previous command

```bash
mkdir /some/long/path
cd !$
# Equivalent to: cd /some/long/path
```

[↑ Back to table of contents](#table-of-contents)

## xargs

Run a command on each line of piped input.

### Remove files by pattern

```bash
find . -name "*.log" | xargs rm
```

### Open files containing a pattern

```bash
grep -rl "TODO" . | xargs code
```

### Handle filenames with spaces

```bash
find . -name "*.txt" -print0 | xargs -0 rm
```

### Limit parallel execution

```bash
find . -name "*.jpg" | xargs -P 4 -I {} convert {} {}.png
```

[↑ Back to table of contents](#table-of-contents)

## Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Git shortcuts
alias gs="git status"
alias gp="git pull"
alias gc="git commit"

# Navigation
alias ..="cd .."
alias ...="cd ../.."

# Utilities
alias ports="lsof -i -P -n | grep LISTEN"
alias myip="curl -s ifconfig.me"

# Safety nets
alias rm="rm -i"
alias mv="mv -i"
alias cp="cp -i"
```

Reload after changes:

```bash
source ~/.bashrc
```

[↑ Back to table of contents](#table-of-contents)

## less

Pipe large output into `less` for navigation:

```bash
ps aux | less
cat largefile.log | less
```

### Navigation keys

| Key | Action |
|:----|:-------|
| `/pattern` | Search forward |
| `?pattern` | Search backward |
| `n` | Next match |
| `N` | Previous match |
| `g` | Go to top |
| `G` | Go to bottom |
| `Space` | Page down |
| `b` | Page up |
| `q` | Quit |

### Useful flags

```bash
less -N file.txt    # Show line numbers
less -S file.txt    # Don't wrap long lines
less +F file.txt    # Follow mode (like tail -f)
```

[↑ Back to table of contents](#table-of-contents)

## Process substitution

Treat command output as a file using `<(command)` syntax:

### Compare directory contents

```bash
diff <(ls dir1) <(ls dir2)
```

### Compare command outputs

```bash
diff <(sort file1.txt) <(sort file2.txt)
```

### Use with commands expecting files

```bash
paste <(cut -f1 file1.txt) <(cut -f2 file2.txt)
```

[↑ Back to table of contents](#table-of-contents)

## tldr

Get simplified, practical examples instead of full man pages.

### Installation

```bash
# npm
npm install -g tldr

# Ubuntu/Debian
apt install tldr

# macOS
brew install tldr
```

### Usage

```bash
tldr tar
tldr find
tldr awk
tldr curl
```

[↑ Back to table of contents](#table-of-contents)

## Directory bookmarks with zoxide

Jump to frequently-used directories with fuzzy matching.

### Installation

```bash
# Using installer script
curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash

# macOS
brew install zoxide

# Ubuntu/Debian
apt install zoxide
```

### Shell configuration

Add to your shell config file:

```bash
# Bash (~/.bashrc)
eval "$(zoxide init bash)"

# Zsh (~/.zshrc)
eval "$(zoxide init zsh)"
```

### Usage

```bash
z project      # Jump to directory matching "project"
z docs         # Jump to directory matching "docs"
zi project     # Interactive selection with fzf
```

Zoxide learns from your navigation patterns and ranks directories by frequency and recency.

[↑ Back to table of contents](#table-of-contents)
