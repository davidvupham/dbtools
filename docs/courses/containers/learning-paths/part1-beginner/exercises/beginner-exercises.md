# Part 1: Beginner Exercises

> **Module:** Part 1 - Beginner | **Type:** Hands-On Practice

Complete these exercises to reinforce your understanding of container basics.

---

## Exercise 1: Container Exploration

**Objective:** Explore running containers and understand their isolation.

### Tasks

1. Run an Ubuntu container interactively:
   ```bash
   docker run -it ubuntu bash
   ```

2. Inside the container, run these commands:
   ```bash
   # Check the OS version
   cat /etc/os-release

   # Check running processes
   ps aux

   # Check network configuration
   ip addr

   # Check hostname
   hostname

   # Create a file
   echo "Hello from container" > /tmp/test.txt

   # Exit the container
   exit
   ```

3. Run another Ubuntu container and verify the file doesn't exist:
   ```bash
   docker run -it ubuntu cat /tmp/test.txt
   # Should fail - file doesn't exist!
   ```

### Questions

- Why doesn't the file exist in the new container?
- What PID is bash running as inside the container?
- How many network interfaces does the container have?

---

## Exercise 2: Port Publishing

**Objective:** Understand how to expose container services.

### Tasks

1. Run nginx without publishing ports:
   ```bash
   docker run -d --name nginx-hidden nginx
   ```

2. Try to access it (this should fail):
   ```bash
   curl http://localhost:80
   # Connection refused
   ```

3. Run nginx with published port:
   ```bash
   docker run -d --name nginx-public -p 8080:80 nginx
   ```

4. Access the web server:
   ```bash
   curl http://localhost:8080
   # Returns nginx welcome page
   ```

5. Check port mappings:
   ```bash
   docker port nginx-public
   ```

6. Clean up:
   ```bash
   docker rm -f nginx-hidden nginx-public
   ```

### Challenge

Run nginx on a random port and find which port was assigned:

```bash
docker run -d --name nginx-random -p 80 nginx
docker port nginx-random
# What port was assigned?
```

---

## Exercise 3: Building Your First Image

**Objective:** Create a custom Docker image.

### Tasks

1. Create a project directory:
   ```bash
   mkdir ~/hello-docker && cd ~/hello-docker
   ```

2. Create a simple Python application:
   ```bash
   cat > app.py << 'EOF'
   from http.server import HTTPServer, SimpleHTTPRequestHandler
   import os

   class MyHandler(SimpleHTTPRequestHandler):
       def do_GET(self):
           self.send_response(200)
           self.send_header('Content-type', 'text/html')
           self.end_headers()
           name = os.environ.get('NAME', 'World')
           self.wfile.write(f'Hello, {name}!'.encode())

   if __name__ == '__main__':
       server = HTTPServer(('0.0.0.0', 8000), MyHandler)
       print('Server running on port 8000...')
       server.serve_forever()
   EOF
   ```

3. Create a Dockerfile:
   ```dockerfile
   # Dockerfile
   FROM python:3.12-slim

   WORKDIR /app

   COPY app.py .

   EXPOSE 8000

   CMD ["python", "app.py"]
   ```

4. Build the image:
   ```bash
   docker build -t hello-docker .
   ```

5. Run the container:
   ```bash
   docker run -d --name hello -p 8000:8000 hello-docker
   ```

6. Test it:
   ```bash
   curl http://localhost:8000
   # Hello, World!
   ```

7. Run with environment variable:
   ```bash
   docker rm -f hello
   docker run -d --name hello -p 8000:8000 -e NAME=Docker hello-docker
   curl http://localhost:8000
   # Hello, Docker!
   ```

### Challenge

Modify the Dockerfile to:
- Add a health check
- Run as non-root user
- Add a label with your name

---

## Exercise 4: Working with Volumes

**Objective:** Understand data persistence with volumes.

### Tasks

1. Create a named volume:
   ```bash
   docker volume create mydata
   ```

2. Run a container and write data:
   ```bash
   docker run --rm -v mydata:/data alpine sh -c "echo 'persistent data' > /data/file.txt"
   ```

3. Verify data in new container:
   ```bash
   docker run --rm -v mydata:/data alpine cat /data/file.txt
   # persistent data
   ```

4. Inspect the volume:
   ```bash
   docker volume inspect mydata
   ```

5. Create a bind mount for development:
   ```bash
   mkdir ~/webfiles
   echo "<h1>My Website</h1>" > ~/webfiles/index.html

   docker run -d --name devweb \
       -v ~/webfiles:/usr/share/nginx/html:ro \
       -p 8080:80 \
       nginx
   ```

6. Modify the file and refresh browser:
   ```bash
   echo "<h1>Updated Website</h1>" > ~/webfiles/index.html
   curl http://localhost:8080
   ```

7. Clean up:
   ```bash
   docker rm -f devweb
   docker volume rm mydata
   ```

### Challenge

Create a backup of a PostgreSQL database volume:

```bash
# Start PostgreSQL with volume
docker volume create pgdata
docker run -d --name pg \
    -e POSTGRES_PASSWORD=secret \
    -v pgdata:/var/lib/postgresql/data \
    postgres:15

# Wait for startup
sleep 10

# Create some data
docker exec pg psql -U postgres -c "CREATE TABLE test (id int); INSERT INTO test VALUES (1);"

# Backup the volume to a tar file (figure out the command!)
# Hint: Use a temporary container with access to both the volume and host filesystem
```

---

## Exercise 5: Container Networking

**Objective:** Connect multiple containers together.

### Tasks

1. Create a custom network:
   ```bash
   docker network create myapp
   ```

2. Start a PostgreSQL database:
   ```bash
   docker run -d --name db --network myapp \
       -e POSTGRES_PASSWORD=secret \
       -e POSTGRES_DB=testdb \
       postgres:15
   ```

3. Wait for database to start:
   ```bash
   docker logs -f db
   # Wait for "database system is ready to accept connections"
   # Ctrl+C to stop following
   ```

4. Connect from another container using DNS:
   ```bash
   docker run -it --rm --network myapp postgres:15 \
       psql -h db -U postgres -d testdb -c "SELECT 1;"
   ```

5. Verify DNS resolution:
   ```bash
   docker run --rm --network myapp alpine ping -c 3 db
   ```

6. Clean up:
   ```bash
   docker rm -f db
   docker network rm myapp
   ```

### Challenge

Create a three-tier application:

```
Frontend (nginx) -> Backend (node) -> Database (postgres)

Requirements:
- Frontend accessible on port 80
- Backend NOT accessible from outside
- Database NOT accessible from outside
- Frontend can reach backend
- Backend can reach database
- Frontend cannot reach database directly

Hint: Use multiple networks!
```

---

## Exercise 6: Image Management

**Objective:** Work with image tags and registries.

### Tasks

1. Pull different nginx versions:
   ```bash
   docker pull nginx:latest
   docker pull nginx:alpine
   docker pull nginx:1.25
   ```

2. Compare sizes:
   ```bash
   docker images nginx
   ```

3. Tag an image for a (fake) registry:
   ```bash
   docker tag nginx:alpine myregistry.com/nginx:alpine
   docker images | grep nginx
   ```

4. View image layers:
   ```bash
   docker history nginx:alpine
   docker history nginx:latest
   ```

5. Save and load an image:
   ```bash
   docker save nginx:alpine -o nginx-alpine.tar
   ls -lh nginx-alpine.tar

   docker rmi nginx:alpine
   docker load -i nginx-alpine.tar
   docker images nginx
   ```

6. Clean up unused images:
   ```bash
   docker image prune -a
   # Type 'y' to confirm
   ```

---

## Exercise 7: Full Stack Application

**Objective:** Deploy a complete application with frontend, backend, and database.

### Tasks

1. Create project structure:
   ```bash
   mkdir -p ~/fullstack-app/{frontend,backend}
   cd ~/fullstack-app
   ```

2. Create backend (Python Flask):
   ```bash
   cat > backend/app.py << 'EOF'
   from flask import Flask, jsonify
   import psycopg2
   import os

   app = Flask(__name__)

   def get_db():
       return psycopg2.connect(os.environ['DATABASE_URL'])

   @app.route('/api/health')
   def health():
       return jsonify(status='healthy')

   @app.route('/api/count')
   def count():
       try:
           conn = get_db()
           cur = conn.cursor()
           cur.execute('SELECT COUNT(*) FROM visits')
           count = cur.fetchone()[0]
           cur.execute('INSERT INTO visits DEFAULT VALUES')
           conn.commit()
           cur.close()
           conn.close()
           return jsonify(count=count + 1)
       except Exception as e:
           return jsonify(error=str(e)), 500

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   EOF

   cat > backend/requirements.txt << 'EOF'
   flask
   psycopg2-binary
   EOF

   cat > backend/Dockerfile << 'EOF'
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY app.py .
   EXPOSE 5000
   CMD ["python", "app.py"]
   EOF
   ```

3. Create frontend (nginx + static HTML):
   ```bash
   cat > frontend/index.html << 'EOF'
   <!DOCTYPE html>
   <html>
   <head><title>Visit Counter</title></head>
   <body>
       <h1>Visit Counter</h1>
       <p>You are visitor #<span id="count">loading...</span></p>
       <script>
           fetch('/api/count')
               .then(r => r.json())
               .then(data => document.getElementById('count').textContent = data.count);
       </script>
   </body>
   </html>
   EOF

   cat > frontend/nginx.conf << 'EOF'
   server {
       listen 80;
       location / {
           root /usr/share/nginx/html;
           index index.html;
       }
       location /api/ {
           proxy_pass http://backend:5000/api/;
       }
   }
   EOF

   cat > frontend/Dockerfile << 'EOF'
   FROM nginx:alpine
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   COPY index.html /usr/share/nginx/html/
   EOF
   ```

4. Build images:
   ```bash
   docker build -t myapp-backend backend/
   docker build -t myapp-frontend frontend/
   ```

5. Create network:
   ```bash
   docker network create myapp-net
   ```

6. Start database:
   ```bash
   docker run -d --name db --network myapp-net \
       -e POSTGRES_PASSWORD=secret \
       -e POSTGRES_DB=myapp \
       postgres:15

   # Wait and create table
   sleep 5
   docker exec db psql -U postgres -d myapp -c \
       "CREATE TABLE visits (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW());"
   ```

7. Start backend:
   ```bash
   docker run -d --name backend --network myapp-net \
       -e DATABASE_URL=postgres://postgres:secret@db:5432/myapp \
       myapp-backend
   ```

8. Start frontend:
   ```bash
   docker run -d --name frontend --network myapp-net \
       -p 80:80 \
       myapp-frontend
   ```

9. Test the application:
   ```bash
   curl http://localhost/
   curl http://localhost/api/count
   curl http://localhost/api/count
   curl http://localhost/api/count
   ```

10. Clean up:
    ```bash
    docker rm -f frontend backend db
    docker network rm myapp-net
    ```

---

## Solutions

Solutions are available in: [solutions/beginner-solutions.md](solutions/beginner-solutions.md)

---

## Next Steps

After completing these exercises, you should be comfortable with:
- Running and managing containers
- Building custom images
- Using volumes for persistence
- Basic container networking

Continue to: [Part 2: Intermediate](../../part2-intermediate/01-docker-compose-basics.md)
