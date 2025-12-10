# Tmux Reference Guide & Cheat Sheet

## Key Definitions
| Term | Definition |
| :--- | :--- |
| **Prefix** | The key combination pressed *before* each tmux command. Default is `Ctrl + b`. **Usage**: Press `Ctrl + b`, release, then press the command key. |
| **Session**| An independent workspace running on the tmux server. |
| **Window** | A "tab" within a session. occupies the full session view. |
| **Pane** | A split section of a window. |

---

## Cheat Sheet

### Session Management
| Command | Description |
| :--- | :--- |
| `tmux new -s <name>` | Start a new session with name `<name>`. |
| `tmux ls` | List running sessions. |
| `tmux a` | Attach to the last used session. |
| `tmux a -t <name>` | Attach to specific session `<name>`. |
| `tmux kill-session -t <name>` | Kills session `<name>`. |
| `prefix + d` | Detach from current session. |
| `prefix + s` | Show all sessions interactively (switch/kill). |
| `prefix + $` | Rename current session. |
| `prefix + ?` | Show all key bindings (press `q` to exit). |

### Window Management
| Command | Description |
| :--- | :--- |
| `prefix + c` | Create new window. |
| `prefix + ,` | Rename current window. |
| `prefix + w` | List windows (interactive menu). |
| `prefix + n` | Next window. |
| `prefix + p` | Previous window. |
| `prefix + 0..9` | Switch to window number 0-9. |
| `prefix + &` | Kill current window (asks confirmation). |

### Pane Management
| Command | Description |
| :--- | :--- |
| `prefix + %` | Split pane vertically (Left/Right). |
| `prefix + "` | Split pane horizontally (Top/Bottom). |
| `prefix + z` | Toggle zoom (maximize/restore) current pane. |
| `prefix + x` | Kill current pane. |
| `prefix + !` | Break pane into its own window. |
| `prefix + {` / `}` | Move pane Left / Right. |
| `prefix + Space` | Toggle between preset layouts. |
| `prefix + q` | Show pane numbers (type number to switch). |
| `prefix + Ctrl + Arrow` | Resize pane in arrow direction (1 cell). |
| `prefix + Alt + Arrow` | Resize pane in arrow direction (5 cells). |

### Copy Mode (Scrollback)
| Command | Description |
| :--- | :--- |
| `prefix + [` | Enter copy mode. |
| `q` | Quit copy mode. |
| **Movement** | Arrows / PgUp / PgDn |
| **Selection** | `Ctrl + Space` (if configured) or drag with mouse. |
| **Copy** | `Alt + w` (default) or `Enter` (vi-mode). |
| `prefix + ]` | Paste copied text. |

---

## Useful Configuration Snippets
Add these to your `~/.tmux.conf`.

### Better Prefix
Remap prefix from `Ctrl+b` to `Ctrl+a` (GNU Screen style).
```tmux
unbind C-b
set -g prefix C-a
bind C-a send-prefix
```

### Config Reload
Reload config without restarting tmux.
```tmux
bind r source-file ~/.tmux.conf \; display "Config Reloaded!"
```

### Mouse Mode
Enable mouse for selecting panes, resizing, and scrolling.
```tmux
set -g mouse on
```

### Split Panes with Current Path
Make new panes open in the same directory as the current one.
```tmux
bind '"' split-window -v -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"
```

### Vi Mode for Copying
Use vim keybindings (h/j/k/l) for navigating copy mode.
```tmux
set-window-option -g mode-keys vi
bind -T copy-mode-vi v send-keys -X begin-selection
bind -T copy-mode-vi y send-keys -X copy-selection-and-cancel
```
