# Chapter 10: Advanced Data & Storage

- Drivers and platforms (local, NFS, cloud drivers)
- tmpfs for ephemeral data
- Strategies for migrations and backups

```bash
# tmpfs example
docker run --rm --read-only --tmpfs /tmp:size=64m myimage:tag
```
