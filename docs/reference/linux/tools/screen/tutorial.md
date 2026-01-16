# Mastering GNU Screen: From Beginner to Advanced

## Introduction
**GNU Screen** is a classic and robust terminal multiplexer. While simpler than tmux, it is ubiquitous—often pre-installed on many server environments where tmux might not be. It allows you to:
-   **Run persistent sessions**: Keep long-running scripts (backups, database migrations) alive after logout.
-   **Manage multiple windows**: Run multiple shell instances in one SSH session.

---

## Part 1: Beginner - Getting Started

### 1. Installation

*   **Ubuntu / Debian**:
    ```bash
    sudo apt update && sudo apt install screen
    ```
*   **Red Hat / CentOS / RHEL / Fedora**:
    ```bash
    sudo dnf install screen
    # For older versions (RHEL 7 / CentOS 7):
    sudo yum install screen
    ```
*   **macOS**:
    Older versions of macOS came with screen. If not found:
    ```bash
    brew install screen
    ```

### 2. Core Concepts
*   **Command Key (Prefix)**: Screen's prefix is **`Ctrl + a`** (written as `C-a`).

    **How to use it (two-step process):**
    1. Press and hold `Ctrl`, tap `a`, then release both keys.
    2. Now press the command key (e.g., `d` to detach).

    For example, `C-a d` means: Press `Ctrl + a` → release → press `d`.

*   **Detaching**: The primary "superpower" of screen. Leaving the session running while you disconnect.

### 3. Your First Session

#### step-by-step
1.  **Start Screen**:
    ```bash
    screen
    ```
    You might see a welcome message. Press `Space` or `Enter` to dismiss it. You are now in a screen session.

2.  **Run a command**:
    Run `top` to visualize the session.

3.  **Detach**:
    Press `Ctrl + a`, release, then press `d`.
    `[detached from 12345.pts-0.hostname]`
    You are back in your host shell. `top` is still running.

4.  **List Sessions**:
    ```bash
    screen -ls
    ```
    You will see a list of sockets, e.g., `12345.pts-0.hostname (Detached)`.

5.  **Reattach**:
    ```bash
    screen -r
    ```
    This reattaches to the first available detached session.

6.  **Force Reattach** (if session is "Attached" elsewhere):
    ```bash
    screen -d -r <name>
    ```
    This detaches the session from any other terminal and reattaches here.

#### Exercises (Beginner)
> [!TIP]
> **Exercise 1: The Safety Net**
> 1. Start a named session: `screen -S myserver`.
> 2. Run a "critical" command: `watch -n 1 date` (simulating a long script).
> 3. Detach (`C-a` then `d`).
> 4. Verify it's running: `screen -ls`.
> 5. Simulate a connection drop: Close your terminal window completely.
> 6. Open a new terminal.
> 7. Reattach: `screen -r myserver`.
> 8. Verify the `watch` command is still running.
> 9. Terminate the session: Stop the command (`Ctrl+c`) and type `exit`.

---

## Part 2: Intermediate - Windows and Regions

### 1. Window Management
Like tabs. Each window runs a separate shell.

*   **Create Window**: `C-a c` (create)
*   **Next Window**: `C-a n` (next) or `C-a Space`
*   **Previous Window**: `C-a p` (previous)
*   **List Windows**: `C-a "` (shows a selectable list)
*   **Switch to Window 0-9**: `C-a 0` ... `C-a 9`

### 2. Split Screen (Regions)
Screen calls splits "regions".

*   **Split Horizontally**: `C-a S` (Shift + s)
*   **Split Vertically**: `C-a |` (Pipe)
*   **Switch Region**: `C-a Tab`
*   **Close Region**: `C-a X` (Shift + x)
*   **Fit Window to Region**: `C-a F` (Resize)

*Note: When you split, the new region is empty. You need to create a window (`C-a c`) or switch to an existing one inside it.*

### 3. Scrollback / Copy Mode
To scroll up to read history, you must enter "Copy Mode".

*   **Enter Copy Mode**: `C-a [` (Escape works too usually)
*   **Navigate**: Arrow keys, PageUp/PageDown.
*   **Quit Copy Mode**: `Esc`

### 4. Configuration (`.screenrc`)
Create `~/.screenrc` to customize behavior.

**Common Settings:**
```bash
# Skip the startup message
startup_message off

# Visible web-browser-like tabs at the bottom
caption always "%{= kw}%-w%{= kG}%{+b}[%n %t]%{-b}%{= kw}%+w"
```

#### Exercises (Intermediate)
> [!TIP]
> **Exercise 2: The Operator**
> 1. Start `screen`.
> 2. Create a horizontal split (`C-a S`).
> 3. Switch to the bottom region (`C-a Tab`).
> 4. It's blank! Create a new window there (`C-a c`).
> 5. Run `htop` in the bottom, leave a shell in the top.
> 6. Practice cycling focus (`C-a Tab`).
> 7. Close the bottom region (`C-a X`).

---

## Part 3: Advanced - Session Sharing & Logging

### 1. Multi-User Mode
Screen allows multiple users to attach to the same session—great for pair programming or admin training.

1.  **Host** sets up permissions:
    *   Enable multi-user: `C-a :multiuser on`
    *   Allow a user (must be logged into the same machine via SSH): `C-a :acladd username`
2.  **Guest** attaches:
    *   `screen -x host_username/session_name`

### 2. Session Logging
Capture all output from your screen session to a file—useful for auditing or debugging.

*   **Toggle Logging**: `C-a H`
    *   Creates a file named `screenlog.0` (or `.1`, `.2`, etc.) in the current directory.
    *   Press again to stop logging.
*   **Start with Logging**: `screen -L -S <name>`

### 3. Kill Session Externally
Terminate a session without attaching to it:
```bash
screen -X -S <name> quit
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
| :--- | :--- |
| "There is a screen on..." (Attached) | Use `screen -d -r <name>` to force detach and reattach. |
| Can't scroll up | Enter copy mode: `C-a [`, then use PageUp/PageDown. |
| New region is blank after split | Regions don't auto-create windows. Use `C-a c` to create one. |
| Screen not found | Install with `sudo apt install screen` or `sudo dnf install screen`. |
| Session won't detach | Ensure you're pressing `C-a`, release, then `d`. |

### SSH Integration
To automatically attach to (or create) a screen session when SSHing:
```bash
ssh -t user@server "screen -d -r main || screen -S main"
```

---

## Video Resources
*   **[GNU Screen Basic Tutorial](https://www.youtube.com/watch?v=ErIsM9D51vw)** by *Install Libre*: Good visual intro.
*   **[How to use GNU SCREEN](https://www.youtube.com/watch?v=hIDj4S8iNfk)** by *Linux Leech*: Comprehensive walkthrough.

---

## See Also
*   [GNU Screen Reference Guide & Cheat Sheet](reference.md) — Quick command lookup.
