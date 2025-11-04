# Chapter 4: Dockerfile Basics

A Dockerfile describes how to build an image.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
```

- Keep images small: use slim bases, `.dockerignore` to exclude junk.
- Layers cache: order steps to maximize cache hits.
- Avoid copying secrets into images.
