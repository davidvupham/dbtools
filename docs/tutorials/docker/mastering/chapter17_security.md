# Chapter 17: Security Hardening

- Run as non‑root (`USER` directive)
- Read‑only filesystem, writable tmpfs as needed
- Drop capabilities and block privilege escalation
- Minimal bases, multi‑stage to exclude build tools
- Secrets via orchestrator or external vaults, not baked into images
- Scan images regularly (Trivy/Grype/Snyk)

```bash
docker run --rm \
  --cap-drop ALL --security-opt no-new-privileges \
  --read-only -v app-tmp:/tmp \
  myimage:tag
```
