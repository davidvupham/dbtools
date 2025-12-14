# Docker Quickstart Guide for Absolute Beginners

## Welcome to Docker

This quickstart guide will have you running Docker containers in **under 15 minutes**. No prior knowledge required!

**What you'll do**:

1. ✅ Install Docker
2. ✅ Run your first container
3. ✅ Build a simple application
4. ✅ Share your image
5. ✅ Run a multi-container application

---

## Prerequisites

- A computer (Windows, Mac, or Linux)
- Internet connection
- Basic command-line knowledge (helpful but not required)

---

## Step 1: Install Docker (5 minutes)

### Windows

1. Visit: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Download **Docker Desktop for Windows**
3. Run the installer
4. Restart your computer when prompted
5. Open Docker Desktop from Start menu
6. Wait for it to start (whale icon in system tray)

### Mac

1. Visit: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Download **Docker Desktop for Mac** (choose Intel or Apple Silicon)
3. Open the `.dmg` file
4. Drag Docker to Applications
5. Open Docker from Applications
6. Wait for it to start (whale icon in menu bar)

### Linux (Ubuntu/Debian)

```bash
# Quick install script (for testing/learning only)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in (or run this)
newgrp docker
```

### Verify Installation

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
docker version
```

You should see version information for both Client and Server. If you do, **Docker is installed!** 🎉

---

## Step 2: Your First Container (2 minutes)

A **container** is like a lightweight virtual machine that runs an application.

### Hello World

```bash
docker run hello-world
```

**What happened?**

1. Docker looked for an image called `hello-world` on your computer
2. Didn't find it, so downloaded it from Docker Hub (the Docker "app store")
3. Created a container from the image
4. Ran the container (which prints a message)
5. Container exited

**Congratulations!** You just ran your first container! 🎉

### Run an Interactive Container

Let's run a container you can interact with:

```bash
docker run -it ubuntu bash
```

**You're now inside a Linux container!** Try these commands:

```bash
# See where you are
pwd

# List files
ls

# Check the OS
cat /etc/os-release

# Exit the container
exit
```

**What just happened?**

- `-it` = Interactive Terminal (lets you type commands)
- `ubuntu` = The image name (a minimal Ubuntu Linux)
- `bash` = The command to run (a shell)

### Run a Web Server

```bash
docker run -d -p 8080:80 --name web nginx
```

Now open your browser and visit: [http://localhost:8080](http://localhost:8080)

**You should see the nginx welcome page!** 🚀

**Command breakdown**:

- `docker run` = Create and start a container
- `-d` = Detached mode (runs in background)
- `-p 8080:80` = Map port 8080 on your computer to port 80 in the container
- `--name web` = Give the container a friendly name
- `nginx` = The image name (a web server)

### Check What's Running

```bash
docker ps
```

This shows all running containers. You should see your nginx container.

### Stop and Remove

```bash
# Stop the container
docker stop web

# Remove the container
docker rm web

# Verify it's gone
docker ps -a
```

---

## Step 3: Build Your First Docker Image (5 minutes)

An **image** is the blueprint for containers. Let's create a simple web application.

### Create a Simple Python Web App

**1. Create a project directory**:

```bash
mkdir my-first-docker-app
cd my-first-docker-app
```

**2. Create a Python application** (`app.py`):

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
        <h1>Hello from Docker!</h1>
        <p>This is my first containerized app! 🐳</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**3. Create requirements file** (`requirements.txt`):

```text
Flask==3.0.0
```

**4. Create a Dockerfile** (`Dockerfile`):

```dockerfile
# Start from a Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
```

**5. Build the image**:

```bash
docker build -t my-first-app .
```

**What happened?**

- `docker build` = Build an image
- `-t my-first-app` = Tag (name) the image
- `.` = Use current directory (where Dockerfile is)

**6. Run your container**:

```bash
docker run -d -p 5000:5000 --name myapp my-first-app
```

**7. Test it**:

Open your browser: [http://localhost:5000](http://localhost:5000)

**You built and ran your own Docker application!** 🎉🎉🎉

**8. View logs**:

```bash
docker logs myapp
```

**9. Stop and remove**:

```bash
docker stop myapp
docker rm myapp
```

---

## Step 4: Share Your Image (Optional)

Want to share your image with others or run it on another machine?

### Create a Docker Hub Account

1. Visit: [https://hub.docker.com](https://hub.docker.com)
2. Sign up for a free account
3. Remember your username

### Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password.

### Tag and Push Your Image

```bash
# Tag your image (replace YOUR_USERNAME)
docker tag my-first-app YOUR_USERNAME/my-first-app:1.0

# Push to Docker Hub
docker push YOUR_USERNAME/my-first-app:1.0
```

**Your image is now on Docker Hub!** Anyone can now pull and run it:

```bash
docker pull YOUR_USERNAME/my-first-app:1.0
docker run -d -p 5000:5000 YOUR_USERNAME/my-first-app:1.0
```

---

## Step 5: Multi-Container Application with Docker Compose (3 minutes)

Real applications often need multiple containers (web server, database, cache, etc.). **Docker Compose** makes this easy.

### Create a WordPress Site with MySQL

**1. Create a new directory**:

```bash
mkdir my-wordpress
cd my-wordpress
```

**2. Create a `docker-compose.yml` file**:

```yaml
version: '3.9'

services:
  # MySQL database
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: wppass
    volumes:
      - db_data:/var/lib/mysql
    restart: always

  # WordPress
  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: wppass
      WORDPRESS_DB_NAME: wordpress
    depends_on:
      - db
    restart: always

volumes:
  db_data:
```

**3. Start the application**:

```bash
docker compose up -d
```

**What happened?**

- Downloaded WordPress and MySQL images
- Created a network for them to communicate
- Created a volume to persist database data
- Started both containers

**4. Open WordPress**:

Visit: [http://localhost:8080](http://localhost:8080)

**You have a full WordPress site running!** 🚀

**5. View running containers**:

```bash
docker compose ps
```

**6. View logs**:

```bash
# All services
docker compose logs

# Just WordPress
docker compose logs wordpress
```

**7. Stop everything**:

```bash
docker compose down
```

**To remove everything including data**:

```bash
docker compose down -v
```

---

## Essential Commands Cheat Sheet

### Images

```bash
docker pull IMAGE                # Download an image
docker images                    # List images on your computer
docker rmi IMAGE                 # Remove an image
docker build -t NAME .           # Build image from Dockerfile
```

### Containers

```bash
docker run IMAGE                 # Create and start a container
docker run -d IMAGE              # Run in background (detached)
docker run -it IMAGE bash        # Run interactively
docker run -p 8080:80 IMAGE      # Map ports (host:container)
docker run --name myname IMAGE   # Give container a name
docker run --rm IMAGE            # Remove container when it stops

docker ps                        # List running containers
docker ps -a                     # List all containers (including stopped)
docker stop CONTAINER            # Stop a container
docker start CONTAINER           # Start a stopped container
docker restart CONTAINER         # Restart a container
docker rm CONTAINER              # Remove a container
docker logs CONTAINER            # View container logs
docker exec -it CONTAINER bash   # Run command in running container
```

### Docker Compose

```bash
docker compose up                # Start all services
docker compose up -d             # Start in background
docker compose ps                # List running services
docker compose logs              # View logs
docker compose stop              # Stop services
docker compose down              # Stop and remove containers
docker compose down -v           # Also remove volumes
```

### Cleanup

```bash
docker system prune              # Remove unused containers, networks, images
docker system prune -a           # Remove ALL unused images
docker container prune           # Remove stopped containers
docker image prune               # Remove unused images
docker volume prune              # Remove unused volumes
```

---

## Common Patterns

### Run a Database for Development

**PostgreSQL**:

```bash
docker run -d \
  --name dev-postgres \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  postgres:15

# Connect with:
# psql -h localhost -U postgres -d myapp
```

**MongoDB**:

```bash
docker run -d \
  --name dev-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 \
  mongo:7

# Connect with:
# mongosh -u admin -p secret
```

**Redis**:

```bash
docker run -d \
  --name dev-redis \
  -p 6379:6379 \
  redis:alpine

# Connect with:
# redis-cli
```

### Quick Testing Different Versions

```bash
# Test Python 3.11
docker run --rm -it python:3.11 python --version

# Test Node.js 20
docker run --rm -it node:20 node --version

# Test Go 1.21
docker run --rm -it golang:1.21 go version
```

### Serve Static Website

```bash
# Put your HTML files in current directory
docker run -d \
  --name static-site \
  -p 8080:80 \
  -v $(pwd):/usr/share/nginx/html:ro \
  nginx:alpine

# Visit: http://localhost:8080
```

---

## Troubleshooting

### "Cannot connect to the Docker daemon"

**Windows/Mac**: Ensure Docker Desktop is running (check system tray/menu bar)

**Linux**:

```bash
sudo systemctl start docker
```

### "Permission denied" (Linux only)

Add your user to the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### "Port is already in use"

Use a different port:

```bash
# Instead of -p 8080:80
docker run -p 8081:80 nginx:alpine
```

### Container Exits Immediately

View logs to see why:

```bash
docker logs CONTAINER_NAME
```

### Out of Disk Space

Clean up unused resources:

```bash
docker system prune -a --volumes
```

### Forgot Container Name

List all containers:

```bash
docker ps -a
```

---

## Next Steps

Congratulations on completing the quickstart! 🎉

**You now know how to**:

- ✅ Run containers
- ✅ Build images
- ✅ Push to Docker Hub
- ✅ Use Docker Compose
- ✅ Run common development services

### Learn More

**For comprehensive learning**, work through the full tutorial:

1. **Foundations** (Start here if new):
   - [Chapter 1: Why Docker?](./chapter01_why_and_how.md)
   - [Chapter 2: Setup](./chapter02_setup.md)
   - [Chapter 3: CLI Essentials](./chapter03_cli_essentials.md)

2. **Building Images**:
   - [Chapter 4: Dockerfile Basics](./chapter04_dockerfile_basics.md)
   - [Chapter 5: Advanced Dockerfile](./chapter05_dockerfile_advanced.md)
   - [Chapter 6: Image Management](./chapter06_image_management.md)

3. **Advanced Topics**:
   - [Chapter 8: Networking](./chapter08_networking.md)
   - [Chapter 9: Volumes and Data](./chapter09_volumes_and_mounts.md)
   - [Chapter 11: Docker Compose](./chapter11_compose_intro.md)

4. **Production**:
   - [Chapter 16: CI/CD](./chapter16_cicd.md)
   - [Chapter 17: Security](./chapter17_security.md)
   - [Chapter 21: JFrog Artifactory](./chapter21_jfrog_artifactory.md)
   - [**New!** Best Practices Guide](./best-practices.md)

### Practice Projects

Try building these applications:

1. **Personal blog** (WordPress + MySQL)
2. **Todo app** (Node.js + MongoDB)
3. **API + Database** (Python Flask + PostgreSQL)
4. **Static site generator** (Hugo/Jekyll + nginx)

### Recommended Learning Path

```text
Week 1: Chapters 1-6  (Foundations and building images)
Week 2: Chapters 7-10 (Containers, networking, data)
Week 3: Chapters 11-14 (Compose and orchestration)
Week 4: Chapters 15-21 (Production, security, enterprise)
```

---

## Helpful Resources

- **Official Documentation**: [docs.docker.com](https://docs.docker.com)
- **Docker Hub**: [hub.docker.com](https://hub.docker.com) - Find images
- **Play with Docker**: [labs.play-with-docker.com](https://labs.play-with-docker.com) - Practice online
- **Community**: [forums.docker.com](https://forums.docker.com)

---

## Quick Reference Card

Save this for easy reference:

| Task | Command |
|------|---------|
| Run container | `docker run IMAGE` |
| Run interactively | `docker run -it IMAGE bash` |
| Run in background | `docker run -d IMAGE` |
| Map port | `docker run -p 8080:80 IMAGE` |
| Name container | `docker run --name myapp IMAGE` |
| List running | `docker ps` |
| List all | `docker ps -a` |
| Stop container | `docker stop CONTAINER` |
| Remove container | `docker rm CONTAINER` |
| View logs | `docker logs CONTAINER` |
| Execute command | `docker exec -it CONTAINER bash` |
| Build image | `docker build -t NAME .` |
| Push image | `docker push NAME` |
| Start compose | `docker compose up -d` |
| Stop compose | `docker compose down` |
| Clean up | `docker system prune` |

---

**Happy Dockering!** 🐳

For questions or issues, refer to the [full tutorial](./README.md) or visit the [Docker forums](https://forums.docker.com).
