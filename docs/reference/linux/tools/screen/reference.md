# GNU Screen reference guide and cheat sheet

**🔗 [← Back to Linux Reference](../../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Screen-blue)

> [!IMPORTANT]
> **Related Docs:** [Screen Tutorial](./tutorial.md) | [Tmux Reference](../tmux/reference.md) | [Bash Reference](../bash/reference.md)

## Key definitions
| Term | Definition |
| :--- | :--- |
| **Prefix (Command Key)** | The key combination pressed *before* each screen command. Default is `Ctrl + a`. **Usage**: Press `Ctrl + a`, release, then press the command key. |
| **Detaching**| Leaving the session running in background while disconnecting from it. |
| **Socket** | The file representation of a running screen session. |

---

## Cheat Sheet

### Session Management
| Command | Description |
| :--- | :--- |
| `screen` | Start a new session. |
| `screen -S <name>` | Start a new named session. |
| `screen -ls` | List running sessions. |
| `screen -r` | Reattach to a detached session. |
| `screen -r <name>` | Reattach to a named session. |
| `screen -d -r <name>` | Force detach from elsewhere and reattach here. |
| `screen -x` | Attach to an *attached* session (Multi-display mode). |
| `screen -X -S <name> quit` | Kill a session externally without attaching. |
| `C-a d` | Detach from current session. |
| `C-a :quit` | Terminate screen session completely. |
| `C-a ?` | Show key binding help. |

### Window Management
| Command | Description |
| :--- | :--- |
| `C-a c` | Create new window. |
| `C-a A` | Rename current window. |
| `C-a "` | List windows (interactive). |
| `C-a n` | Next window. |
| `C-a p` | Previous window. |
| `C-a 0..9` | Switch to window number 0-9. |
| `C-a k` | Kill current window. |

### Region Management (Splits)
| Command | Description |
| :--- | :--- |
| `C-a S` | Split region horizontally. |
| `C-a |` | Split region vertically. |
| `C-a Tab` | Switch focus to next region. |
| `C-a X` | Kill current region. |
| `C-a Q` | Kill all regions except current one. |

### Copy Mode (Scrollback)
| Command | Description |
| :--- | :--- |
| `C-a [` | Enter copy/scrollback mode. |
| `Esc` | Quit copy mode. |
| **Movement** | Arrows / PgUp / PgDn |
| **Start Select** | `Space` |
| **End Select** | `Space` again (copies to buffer). |
| `C-a ]` | Paste buffer. |

### Logging
| Command | Description |
| :--- | :--- |
| `C-a H` | Toggle logging to `screenlog.N` file. |
| `screen -L` | Start screen with logging enabled. |

---

## Configuration (`.screenrc`)
Common useful settings for `~/.screenrc`:

```screen
# Turn off the splash screen
startup_message off

# Use visual bell (flash) instead of audio beep
vbell on

# A solid status bar at the bottom
hardstatus alwayslastline
hardstatus string '%{= kG}[ %{G}%H %{g}][%= %{= kw}%?%-Lw%?%{r}(%{W}%n*%f%t%?(%u)%?%{r})%{w}%?%+Lw%?%?%= %{g}][%{B} %d/%m %{W}%c %{g}]'
```
