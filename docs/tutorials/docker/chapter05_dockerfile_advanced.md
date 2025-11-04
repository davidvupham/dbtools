# Chapter 5: Advanced Dockerfile Techniques

Multi‑stage builds let you compile in one image and ship only the runtime.

```dockerfile
FROM golang:1.22-alpine AS build
WORKDIR /src
COPY . .
RUN go build -o app ./...

FROM alpine:3.19
WORKDIR /app
COPY --from=build /src/app ./app
RUN adduser -D appuser
USER appuser
ENTRYPOINT ["./app"]
```

- Use `ARG`/`ENV` for build/runtime parameters.
- Prefer `RUN apt-get update && apt-get install ... && rm -rf /var/lib/apt/lists/*` in one layer.
- Consider distroless/minimal bases for fewer CVEs.
