# First Dockerfile Example

> **Level:** Beginner | **Time:** 15 minutes

## Overview

This example shows how to create your first Dockerfile and build a custom image.

## Project Structure

```
first-dockerfile/
├── Dockerfile
├── index.html
└── README.md
```

## Files

### index.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>My First Container</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello from my first Dockerfile!</h1>
        <p>This page is served from a custom container.</p>
        <p>Built with Docker/Podman</p>
    </div>
</body>
</html>
```

### Dockerfile

```dockerfile
# Use nginx as the base image
FROM nginx:alpine

# Copy our custom HTML file
COPY index.html /usr/share/nginx/html/index.html

# Document that container listens on port 80
EXPOSE 80

# nginx starts automatically (CMD inherited from base image)
```

## Build and Run

### Step 1: Build the Image

```bash
# Navigate to this directory
cd examples/beginner/first-dockerfile

# Build the image
docker build -t my-first-image .

# Verify the image was created
docker images my-first-image
```

### Step 2: Run the Container

```bash
# Run the container
docker run -d --name my-first-container -p 8080:80 my-first-image

# Check it's running
docker ps
```

### Step 3: Access the Application

```bash
# Using curl
curl http://localhost:8080

# Or open in browser
# http://localhost:8080
```

### Step 4: View Build Layers

```bash
# See the image layers
docker history my-first-image
```

Output:
```
IMAGE          CREATED          CREATED BY                                      SIZE
abc123         1 minute ago     COPY index.html /usr/share/nginx/html/...      1.5kB
def456         2 weeks ago      /bin/sh -c #(nop)  CMD ["nginx" "-g" "daemon…   0B
...
```

## Cleanup

```bash
# Stop and remove container
docker rm -f my-first-container

# Remove image
docker rmi my-first-image
```

## Key Points

1. **FROM** specifies the base image
2. **COPY** adds files from your computer to the image
3. **EXPOSE** documents which port the app uses
4. **Build context** (the `.`) is where Docker looks for files

## Exercises

1. Modify `index.html` and rebuild the image
2. Add a second HTML file and access it at `/about.html`
3. Try using `nginx:latest` instead of `nginx:alpine` and compare image sizes

## Next Steps

- [Simple Web Server](../simple-web-server/)
- [Multi-stage Builds](../../intermediate/multi-stage-build/)
