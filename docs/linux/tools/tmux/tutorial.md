# Mastering Tmux: From Beginner to Advanced

## Introduction
**Tmux** (Terminal Multiplexer) is a productivity tool that allows you to manage multiple terminal sessions within a single window. It enables you to:
-   **Run persistent sessions**: Keep programs running even if you disconnect.
-   **Manage windows and panes**: Split your terminal into multiple workable areas.
-   **Pair program**: Share sessions with other users (advanced).

This tutorial is designed to take you from a complete beginner to an advanced user.

---

## Part 1: Beginner - Getting Started

### 1. Installation

*   **Ubuntu / Debian**:
    ```bash
    sudo apt update && sudo apt install tmux
    ```
*   **Red Hat / CentOS / RHEL / Fedora**:
    ```bash
    sudo dnf install tmux
    # For older versions (RHEL 7 / CentOS 7):
    sudo yum install tmux
    ```
*   **macOS**:
    ```bash
    brew install tmux
    ```
*   **Windows (WSL)**:
    Tmux runs natively on Linux. Ensure you have WSL enabled and a distro like Ubuntu installed, then follow the Ubuntu instructions inside your WSL terminal.

### 2. Core Concepts
*   **Server**: The backend process that holds all sessions.
*   **Session**: A single workspace. Detaching from a session leaves it running on the server.
*   **Window**: Like tabs in a browser or editor. A session can have multiple windows.
*   **Pane**: A division within a window. You can split a window into multiple panes.

### 3. Your First Session
The most important concept in tmux is the **Prefix Key**. By default, it is **`Ctrl + b`**.

**How to use it (two-step process):**
1. Press and hold `Ctrl`, tap `b`, then release both keys.
2. Now press the command key (e.g., `d` to detach).

For example, to detach from a session, the documentation says `prefix + d`. This means:
- Press `Ctrl + b` → release → press `d`

> [!TIP]
> **Quick Help**: Press `prefix + ?` at any time to see all available key bindings.

#### step-by-step
1.  **Start tmux**:
    ```bash
    tmux
    ```
    You are now inside a tmux session. Notice the green status bar at the bottom.

2.  **Run a command**:
    Run `top` or `htop` to see something moving.

3.  **Detach**:
    Press `Ctrl + b` then `d`.
    You are back in your normal shell. The `top` command is still running in the background!

4.  **List Sessions**:
    ```bash
    tmux ls
    ```
    You will see something like `0: 1 windows (created ...)`

5.  **Reattach**:
    ```bash
    tmux attach -t 0
    ```
    (Replace `0` with the name of session if different). You are back in your session with `top` running.

#### Exercises (Beginner)
> [!TIP]
> **Exercise 1: Session Juggler**
> 1. Start a new named session: `tmux new -s work`.
> 2. Run a command (e.g., `echo "I am working"`).
> 3. Detach (`prefix + d`).
> 4. Create another session: `tmux new -s play`.
> 5. Detach.
> 6. List sessions (`tmux ls`).
> 7. Kill the 'play' session: `tmux kill-session -t play`.

---

## Part 2: Intermediate - Layouts and Config

### 1. Window Management
Stop using multiple terminal tabs. Use tmux windows instead.

*   **Create Window**: `prefix + c`
*   **Next Window**: `prefix + n`
*   **Previous Window**: `prefix + p`
*   **Rename Window**: `prefix + ,`
*   **List/Select Window**: `prefix + w` (Navigate with arrow keys, Enter to select)

### 2. Pane Management
Splitting one window into multiple concurrent terminals.

*   **Split Vertically**: `prefix + %`
*   **Split Horizontally**: `prefix + "`
*   **Navigate Panes**: `prefix + Arrow Keys`
*   **Close Pane**: Type `exit` or `prefix + x`
*   **Zoom Pane**: `prefix + z` (Makes current pane full screen. Press again to restore).

### 3. Copy Mode & Scrollback
Since tmux is a TUI (Text User Interface), you can't always just scroll up with your mouse wheel comfortably. You need **Copy Mode**.

*   **Enter Copy Mode**: `prefix + [`
*   **Navigate**: Use Arrow keys, PageUp/PageDown.
*   **Quit Copy Mode**: `q`

*(Note: Advanced configuration allows Vim-style navigation here)*

### 4. Configuration (`.tmux.conf`)
You can customize tmux by creating a file named `.tmux.conf` in your home user directory (`~/.tmux.conf`).

**Common Settings:**
```tmux
# Change Host Key from Ctrl+b to Ctrl+a (easier to reach)
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Enable Mouse support (Clicking panes, scrolling)
set -g mouse on
```
*After editing the file, reload it from within tmux by typing command mode: `prefix + :`, then `source-file ~/.tmux.conf`.*

#### Exercises (Intermediate)
> [!TIP]
> **Exercise 2: The Dev Dashboard**
> 1. Create a session named `dashboard`.
> 2. Rename the first window to `monitor`.
> 3. Split the window horizontally.
> 4. Split the bottom pane vertically. You now have 3 panes.
> 5. Run `top` in one, `df -h` in another, and keep a shell prompt in the third.
> 6. Create a new window named `editor`.
> 7. Detach and reattach to verify everything is still there.

---

## Part 3: Advanced - Plugins and Scripting

### 1. Tmux Plugin Manager (TPM)
Just like packages for your OS, tmux has plugins. The standard way to manage them is TPM.

**Installation**:
```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

**Setup in `~/.tmux.conf`**:
```tmux
# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'

# Initialize TMUX plugin manager (keep this line at the very bottom of tmux.conf)
run '~/.tmux/plugins/tpm/tpm'
```
*Reload tmux config (`prefix + : source-file ~/.tmux.conf`), then press `prefix + I` (capital i) to install plugins.*

### 2. Essential Plugins
*   **tmux-resurrect**: Persist sessions across system restarts.
    *   Save: `prefix + Ctrl-s`
    *   Restore: `prefix + Ctrl-r`
*   **tmux-continuum**: Automatically saves sessions.

### 3. Scripting Workflows
Stop setting up your panes manually every day. Use a bash script to launch your environment.

**Example `dev-env.sh`**:
```bash
#!/bin/bash
SESSION="myproject"

tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then
  tmux new-session -d -s $SESSION -n "editor"
  tmux send-keys -t $SESSION:1 "vim" C-m
  
  tmux new-window -t $SESSION -n "server"
  tmux send-keys -t $SESSION:2 "npm run start" C-m
  
  tmux select-window -t $SESSION:1
fi

tmux attach -t $SESSION
```

#### Exercises (Advanced)
> [!TIP]
> **Exercise 3: The Automator**
> 1. Install TPM and `tmux-resurrect`.
> 2. Create the layout from Exercise 2.
> 3. Save the session with `tmux-resurrect`.
> 4. Kill the tmux server entirely (`tmux kill-server`).
> 5. Start tmux again and restore your layout using `prefix + Ctrl-r`.
> 6. (Optional) Write a bash script to spin up this specific layout automatically.

---

## Troubleshooting

### Common Issues

| Problem | Solution |
| :--- | :--- |
| "sessions should be nested..." error | You're already inside tmux. Detach first or use `TMUX= tmux` to force. |
| Colors look wrong | Ensure `TERM=xterm-256color` in your shell. Add `set -g default-terminal "screen-256color"` to `.tmux.conf`. |
| Prefix key not responding | Verify prefix with `tmux show -g prefix`. Check for conflicts with shell bindings. |
| Session attached elsewhere | Use `tmux attach -d -t <name>` to force detach from other client. |
| Can't scroll with mouse | Add `set -g mouse on` to `.tmux.conf` and reload. |

### Kill All Sessions
```bash
tmux kill-server
```
This terminates all tmux sessions and the server process.

### SSH Integration
To automatically attach to (or create) a tmux session when SSHing into a server:
```bash
ssh -t user@server "tmux attach -t main || tmux new -s main"
```

---

## Video Resources
If you prefer learning through video, here are some excellent community tutorials:

### Beginner / Quick Start
*   **[Tmux in 100 Seconds](https://www.youtube.com/watch?v=Mg9yaIzgweA)** by *Fireship*: Quick overview of what and why.
*   **[Tmux Tutorial for Beginners](https://www.youtube.com/watch?v=BHhA_ZKjykE)** by *Linux Training Academy*: Solid walkthrough of basics.

### Workflow & Productivity
*   **[Tmux will SKYROCKET your productivity](https://www.youtube.com/watch?v=DzNmUNvnB04)** by *Typecraft*: Real-world developer workflow.

### Advanced & Customization
*   **[Making Tmux Better AND Beautiful](https://www.youtube.com/watch?v=GH3kWd3k6U0)** by *Dreams of Code*: Customization and aesthetics.
*   **[Tmux From Scratch To BEAST MODE](https://www.youtube.com/watch?v=C7Yi1O7ZbTw)** by *omerxx*: Advanced setup guide.

---

## See Also
*   [Tmux Reference Guide & Cheat Sheet](reference.md) — Quick command lookup.
