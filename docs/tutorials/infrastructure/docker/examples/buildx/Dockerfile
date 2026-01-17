# syntax=docker/dockerfile:1.6

# Build stage
FROM --platform=$BUILDPLATFORM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod go.sum* ./
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go version >/dev/null 2>&1 || true
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=$(echo $TARGETOS) GOARCH=$(echo $TARGETARCH) go build -o /out/app ./...

# Final image: minimal
FROM gcr.io/distroless/static:nonroot
COPY --from=build /out/app /app
USER 65532
EXPOSE 8080
ENTRYPOINT ["/app"]
