# Lab 02: Building Container Images

> **Level:** Beginner | **Time:** 60-75 minutes | **Prerequisites:** Lab 01 completed

## Lab Overview

In this lab, you will learn to create custom container images using Dockerfiles. You'll build images for different applications and learn optimization techniques.

---

## Learning Objectives

By completing this lab, you will be able to:

- Write Dockerfiles with essential instructions
- Build images from Dockerfiles
- Understand layer caching
- Optimize Dockerfiles for smaller images
- Tag and manage custom images

---

## Prerequisites

- Completed Lab 01
- Docker or Podman installed
- Text editor available
- Basic understanding of application runtimes

---

## Part 1: Your First Dockerfile

### Task 1.1: Create Project Structure

```bash
mkdir -p ~/docker-lab/simple-app && cd ~/docker-lab/simple-app
```

### Task 1.2: Create a Simple Application

Create `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My First Container</title>
</head>
<body>
    <h1>Hello from Docker!</h1>
    <p>This page is served from a custom container.</p>
</body>
</html>
```

### Task 1.3: Write the Dockerfile

Create `Dockerfile`:

```dockerfile
# Use nginx as base image
FROM nginx:alpine

# Copy our content
COPY index.html /usr/share/nginx/html/

# Document the port
EXPOSE 80

# nginx starts automatically (inherited from base image)
```

### Task 1.4: Build the Image

```bash
docker build -t my-nginx:v1 .
```

**Observe the output:**
- Each instruction creates a layer
- Layers are cached for future builds

### Task 1.5: Test the Image

```bash
# Run the container
docker run -d --name mynginx -p 8080:80 my-nginx:v1

# Test
curl http://localhost:8080

# Cleanup
docker rm -f mynginx
```

---

## Part 2: Building a Python Application

### Task 2.1: Create Project Structure

```bash
mkdir -p ~/docker-lab/python-app && cd ~/docker-lab/python-app
```

### Task 2.2: Create the Application

Create `app.py`:

```python
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Python!',
        'hostname': socket.gethostname(),
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Create `requirements.txt`:

```
flask==3.0.0
```

### Task 2.3: Write the Dockerfile

Create `Dockerfile`:

```dockerfile
# Use Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Set environment variable
ENV ENVIRONMENT=production

# Document port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
```

### Task 2.4: Build and Test

```bash
# Build
docker build -t python-app:v1 .

# Run
docker run -d --name pyapp -p 5000:5000 python-app:v1

# Test
curl http://localhost:5000
curl http://localhost:5000/health

# Cleanup
docker rm -f pyapp
```

---

## Part 3: Understanding Layer Caching

### Task 3.1: Modify the Application

Edit `app.py` to change the message:

```python
'message': 'Hello from Python! (v2)',
```

### Task 3.2: Rebuild and Observe Caching

```bash
docker build -t python-app:v2 .
```

**Notice:**
- Layers before `COPY app.py` are cached
- Only the last layer is rebuilt

### Task 3.3: Break the Cache

Modify `requirements.txt` (add a comment or new package):

```
flask==3.0.0
# This comment breaks the cache
```

Rebuild:

```bash
docker build -t python-app:v3 .
```

**Notice:** The `pip install` layer is rebuilt.

---

## Part 4: Multi-Stage Builds

### Task 4.1: Create a Node.js Project

```bash
mkdir -p ~/docker-lab/node-app && cd ~/docker-lab/node-app
```

Create `package.json`:

```json
{
  "name": "node-app",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

Create `server.js`:

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({
        message: 'Hello from Node.js!',
        version: process.version
    });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

### Task 4.2: Single-Stage Dockerfile (Larger)

Create `Dockerfile.single`:

```dockerfile
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

Build and check size:

```bash
docker build -f Dockerfile.single -t node-app:single .
docker images node-app:single
```

### Task 4.3: Multi-Stage Dockerfile (Smaller)

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

Build and compare:

```bash
docker build -t node-app:multi .
docker images node-app
```

---

## Part 5: Dockerfile Best Practices

### Task 5.1: Add a Non-Root User

Modify the Python Dockerfile:

```dockerfile
FROM python:3.12-slim

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py .

# Switch to non-root user
USER appuser

ENV ENVIRONMENT=production
EXPOSE 5000
CMD ["python", "app.py"]
```

### Task 5.2: Add Health Check

```dockerfile
FROM python:3.12-slim

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py .

USER appuser

ENV ENVIRONMENT=production
EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

### Task 5.3: Add Labels

```dockerfile
FROM python:3.12-slim

LABEL maintainer="your@email.com"
LABEL version="1.0"
LABEL description="Python Flask application"

# ... rest of Dockerfile
```

---

## Part 6: Using .dockerignore

### Task 6.1: Create .dockerignore

In your project directory, create `.dockerignore`:

```
.git
.gitignore
*.md
__pycache__
*.pyc
.pytest_cache
.coverage
venv
.env
*.log
node_modules
.npm
Dockerfile*
docker-compose*.yml
```

### Task 6.2: Test the Effect

```bash
# Create some files to ignore
mkdir -p .git node_modules
touch test.log .env

# Build and check context size
docker build -t test-ignore .
```

---

## Part 7: Challenge Exercises

### Challenge 1: Go Application

Create a multi-stage build for a Go application that results in a ~10MB image:

1. Create a simple Go HTTP server
2. Build it with multi-stage using `golang:1.22` and `scratch`
3. The final image should only contain the static binary

### Challenge 2: Python with Build Dependencies

Create a Dockerfile for a Python app that:
- Needs compilation (e.g., `numpy`, `pandas`)
- Uses multi-stage to keep the final image small
- Runs as non-root user

### Challenge 3: Optimize an Existing Dockerfile

Given this inefficient Dockerfile, optimize it:

```dockerfile
FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install gunicorn
EXPOSE 5000
CMD ["python3", "app.py"]
```

---

## Verification Checklist

- [ ] Built a custom nginx image
- [ ] Built a Python Flask application image
- [ ] Demonstrated layer caching behavior
- [ ] Created a multi-stage build
- [ ] Added non-root user to image
- [ ] Added health check
- [ ] Created .dockerignore file

---

## Cleanup

```bash
# Remove lab containers
docker rm -f $(docker ps -aq)

# Remove lab images
docker rmi my-nginx:v1 python-app:v1 python-app:v2 python-app:v3 node-app:single node-app:multi

# Remove unused images
docker image prune -f
```

---

## Solutions

See [solutions.md](solutions.md) for detailed solutions.

---

## Next Lab

Continue to: [Lab 03: Networking](../lab03-networking/)
