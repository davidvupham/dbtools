# Chapter 12: Advanced Compose

- Profiles for dev/prod variants
- Overrides and environment files
- Scaling services

```yaml
services:
  web:
    image: myorg/web:1.0
    profiles: ["dev"]
```

```bash
docker compose --profile dev up -d
```
