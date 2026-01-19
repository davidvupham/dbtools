# DCA exam preparation

> **Module:** Certification | **Level:** Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Understand exam format and requirements
- Create a study plan
- Access practice resources
- Apply test-taking strategies

---

## Exam overview

### Exam details

| Aspect | Details |
|--------|---------|
| **Name** | Docker Certified Associate (DCA) |
| **Duration** | 90 minutes |
| **Questions** | 55 multiple choice |
| **Passing score** | 65% (approximately 36 questions) |
| **Format** | Online, proctored |
| **Validity** | 2 years |
| **Cost** | ~$195 USD |
| **Retake** | After 14 days |

### Registration

Register at: [https://training.mirantis.com/certification/dca-certification-exam/](https://training.mirantis.com/certification/dca-certification-exam/)

---

## Domain breakdown

### 1. Orchestration (25%)

Topics:
- Docker Swarm architecture
- Service creation and management
- Stacks and compose files
- Networking in Swarm
- High availability

Key commands:
```bash
docker swarm init
docker service create
docker stack deploy
docker node ls
```

### 2. Image creation and management (20%)

Topics:
- Dockerfile best practices
- Multi-stage builds
- Image layers and caching
- Registry operations
- Image security

Key commands:
```bash
docker build
docker tag
docker push/pull
docker image inspect
```

### 3. Installation and configuration (15%)

Topics:
- Docker Engine installation
- Storage drivers
- Logging configuration
- Networking configuration
- Security configuration

Key files:
```bash
/etc/docker/daemon.json
~/.docker/config.json
/etc/systemd/system/docker.service.d/
```

### 4. Networking (15%)

Topics:
- Network drivers (bridge, overlay, macvlan)
- DNS and service discovery
- Load balancing
- Network troubleshooting

Key commands:
```bash
docker network create
docker network inspect
docker network connect
```

### 5. Security (15%)

Topics:
- Image scanning
- Secrets management
- TLS configuration
- User namespaces
- Content trust

Key commands:
```bash
docker secret create
docker trust sign
docker scan
```

### 6. Storage and volumes (10%)

Topics:
- Volume types and drivers
- Bind mounts
- Storage drivers
- Backup and restore

Key commands:
```bash
docker volume create
docker volume inspect
docker run -v
```

---

## Study plan

### Week 1-2: Fundamentals

- [ ] Review Docker architecture
- [ ] Practice basic commands
- [ ] Understand image layers
- [ ] Learn Dockerfile optimization

### Week 3-4: Orchestration

- [ ] Set up Docker Swarm
- [ ] Create and manage services
- [ ] Deploy stacks
- [ ] Practice scaling and updates

### Week 5-6: Networking & storage

- [ ] Create custom networks
- [ ] Understand overlay networking
- [ ] Practice volume management
- [ ] Test backup/restore procedures

### Week 7-8: Security & final prep

- [ ] Implement secrets management
- [ ] Configure TLS
- [ ] Take practice exams
- [ ] Review weak areas

---

## Practice labs

### Lab 1: Build and push image

```bash
# Create efficient Dockerfile
cat << 'EOF' > Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
EOF

# Build and tag
docker build -t myapp:v1 .
docker tag myapp:v1 registry.example.com/myapp:v1
docker push registry.example.com/myapp:v1
```

### Lab 2: Set up Swarm cluster

```bash
# Initialize swarm
docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')

# Create overlay network
docker network create --driver overlay --attachable app-net

# Deploy service
docker service create \
    --name api \
    --replicas 3 \
    --network app-net \
    --publish published=80,target=5000 \
    --update-parallelism 1 \
    --update-delay 10s \
    myapp:v1

# Check service
docker service ps api
docker service logs api
```

### Lab 3: Secrets management

```bash
# Create secrets
echo "mysecretpassword" | docker secret create db_password -
docker secret create ssl_cert ./server.crt

# Use in service
docker service create \
    --name api \
    --secret db_password \
    --secret source=ssl_cert,target=/etc/ssl/server.crt \
    myapp:v1
```

---

## Sample questions

### Question 1

What is the correct way to limit a container to 512MB of memory?

- A) `docker run --memory-limit 512m nginx`
- B) `docker run -m 512m nginx`
- C) `docker run --mem 512m nginx`
- D) `docker run --limit-memory 512m nginx`

**Answer: B**

### Question 2

Which command displays the layers of a Docker image?

- A) `docker image layers nginx`
- B) `docker inspect nginx`
- C) `docker history nginx`
- D) `docker image show nginx`

**Answer: C**

### Question 3

In Docker Swarm, what is the purpose of the routing mesh?

- A) To encrypt all network traffic
- B) To enable service discovery
- C) To route traffic to service tasks regardless of which node receives the request
- D) To create overlay networks

**Answer: C**

### Question 4

What is the default network driver for Docker?

- A) host
- B) overlay
- C) bridge
- D) macvlan

**Answer: C**

### Question 5

Which file is used to configure the Docker daemon?

- A) /etc/docker/config.json
- B) /etc/docker/daemon.json
- C) /var/lib/docker/config.json
- D) ~/.docker/daemon.json

**Answer: B**

---

## Test-taking strategies

### Before the exam

1. **Get hands-on experience** - Don't just read, practice
2. **Set up a lab environment** - Use VMs or cloud instances
3. **Take practice exams** - Time yourself
4. **Review official documentation** - Primary source of truth

### During the exam

1. **Read carefully** - Questions can be tricky
2. **Manage time** - ~1.6 minutes per question
3. **Flag difficult questions** - Return later
4. **Eliminate wrong answers** - Improve odds
5. **Don't overthink** - First instinct is often right

### Command memorization

Focus on these flags:
- `docker run`: -d, -it, -p, -v, --name, --network, -e, --rm
- `docker service create`: --replicas, --publish, --network, --secret
- `docker stack deploy`: -c, --prune
- `docker build`: -t, -f, --no-cache, --target

---

## Resources

### Official

- [Docker Documentation](https://docs.docker.com/)
- [Docker Certified Associate Study Guide](https://training.mirantis.com/dca-study-guide/)

### Practice

- [Play with Docker](https://labs.play-with-docker.com/)
- [Katacoda Docker Scenarios](https://www.katacoda.com/courses/docker)

### Community

- Docker Community Forums
- Stack Overflow [docker] tag
- Reddit r/docker

---

## Key takeaways

1. **Hands-on practice** is essential
2. **Focus on orchestration** - 25% of exam
3. **Know the commands** and their flags
4. **Understand networking** deeply
5. **Practice with time limits**

---

## What's next

Review the exam topic checklist.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [DCA Overview](01-dca-overview.md) | [Course Overview](../course_overview.md) | [Exam Checklist](03-exam-checklist.md) |
