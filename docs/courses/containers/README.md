# Containers Course

> **Master Docker, Podman, and OpenShift from Zero to Certification**

A comprehensive, beginner-to-advanced course on container technology. No prior container knowledge required.

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [Course Overview](course_overview.md) | Learning objectives, prerequisites, time estimates |
| [Quick Reference](quick_reference.md) | Docker & Podman command cheat sheet |
| [Glossary](glossary.md) | Container terminology (50+ terms) |
| [DCA Exam Registration](https://training.mirantis.com/certification/dca-certification-exam/) | Official certification signup ($195 USD) |

---

## Learning Paths

### Path A: Complete Course (10 weeks)

The recommended path for comprehensive mastery.

```
Week 1:  concepts/ + part1-beginner/ (01-05)
Week 2:  part1-beginner/ (06-09) + Lab 1-2 + Quiz
Week 3:  part2-intermediate/ (01-05) + Lab 3
Week 4:  part2-intermediate/ (06-10) + Lab 4-5 + Quiz
Week 5:  storage/ + networking/ + Labs + Quizzes
Week 6:  rootless/ + security/ + Labs + Quizzes
Week 7:  part3-advanced/ (01-07) + Lab 6-7
Week 8:  part3-advanced/ (08-14) + Lab 8-9 + Quiz
Week 9:  kubernetes-essentials/ + operations/ + Quizzes
Week 10: certification/ + Practice exams + emerging/ (bonus)
```

### Path B: Quick Start (2 weeks)

Get productive with containers fast.

```
Week 1: concepts/01-02 + part1-beginner/ + Quiz
Week 2: part2-intermediate/01-09 + Lab 5 + Quiz
```

### Path C: DCA Exam Focus (6 weeks)

Optimized for Docker Certified Associate certification.

```
Week 1: concepts/ + part1-beginner/
Week 2: part2-intermediate/
Week 3: storage/ + networking/
Week 4: security/ + rootless/
Week 5: part3-advanced/ (orchestration focus)
Week 6: kubernetes-essentials/ + operations/ + practice exams
```

### Path D: Security Deep Dive (3 weeks)

For security-focused professionals.

```
Week 1: concepts/05-06 + rootless/
Week 2: security/ + CIS Benchmark review
Week 3: emerging/supply-chain-security.md + emerging/distroless-images.md
```

### Path E: OpenShift Focus (3 weeks)

For teams adopting Red Hat OpenShift.

```
Week 1: kubernetes-essentials/ + openshift/01-04 (Introduction, Concepts, CLI, S2I)
Week 2: openshift/05-07 (Security, Networking, Operators)
Week 3: openshift/08 + Quiz + Practice with OpenShift Local
```

---

## Course Modules

### Foundational Theory

| Module | Description | Files |
|--------|-------------|-------|
| [concepts/](concepts/) | Container fundamentals, OCI standards, architecture | 7 |

### Learning Paths (Sequential)

| Module | Level | Description | Files |
|--------|-------|-------------|-------|
| [part1-beginner/](learning-paths/part1-beginner/) | Beginner | First containers, Dockerfiles, basic volumes | 9 + quiz |
| [part2-intermediate/](learning-paths/part2-intermediate/) | Intermediate | Networking, storage, Compose, pods | 10 + quiz |
| [part3-advanced/](learning-paths/part3-advanced/) | Advanced | Rootless, Swarm, CI/CD, enterprise | 14 + quiz |
| [kubernetes-essentials/](kubernetes-essentials/) | Advanced | K8s for DCA exam | 6 + quiz |
| [openshift/](openshift/) | Intermediate-Advanced | Red Hat OpenShift platform | 8 + quiz |

### Deep Dive Modules

| Module | Description | Files |
|--------|-------------|-------|
| [storage/](storage/) | Image locations, drivers, configuration | 9 + quiz |
| [networking/](networking/) | Drivers, DNS, overlay, troubleshooting | 9 + quiz |
| [rootless/](rootless/) | UID mapping, permissions, networking | 10 + quiz |
| [security/](security/) | DCT, scanning, MTLS, secrets, RBAC | 10 + quiz |
| [operations/](operations/) | Logging, backup, HA, troubleshooting | 6 + quiz |

### Reference & Comparison

| Module | Description | Files |
|--------|-------------|-------|
| [comparison/](comparison/) | Docker vs Podman side-by-side | 7 |
| [reference/](learning-paths/reference/) | Command tables, Dockerfile syntax, Compose | 4 |

### Certification & Emerging Topics

| Module | Description | Files |
|--------|-------------|-------|
| [certification/](certification/) | DCA exam prep, practice resources | 4 |
| [emerging/](emerging/) | Wasm, AI/LLM, devcontainers, supply chain | 7 |

---

## Hands-on Labs

| Lab | Topic | Duration |
|-----|-------|----------|
| [Lab 1](labs/lab01-container-basics/) | Container basics | 45 min |
| [Lab 2](labs/lab02-building-images/) | Building images | 60 min |
| [Lab 3](labs/lab03-networking/) | Container networking | 60 min |
| [Lab 4](labs/lab04-volumes-storage/) | Volumes and storage | 45 min |
| [Lab 5](labs/lab05-compose-application/) | Multi-container Compose app | 90 min |
| [Lab 6](labs/lab06-rootless-permissions/) | Rootless permissions | 60 min |
| [Lab 7](labs/lab07-swarm-cluster/) | Swarm cluster setup | 90 min |
| [Lab 8](labs/lab08-security-hardening/) | Security hardening | 60 min |
| [Lab 9](labs/lab09-troubleshooting/) | Troubleshooting scenarios | 60 min |

---

## Lab Environment Options

| Platform | Features | Link |
|----------|----------|------|
| **Play with Docker** | Free, browser-based, 4hr sessions | [labs.play-with-docker.com](https://labs.play-with-docker.com/) |
| **LabEx** | VS Code interface, persistent | [labex.io](https://labex.io/tutorials/docker-online-docker-playground-372912) |
| **iximiuz Labs** | Auto-graded, multi-node | [labs.iximiuz.com](https://labs.iximiuz.com) |
| **Local** | Docker Desktop or Podman Desktop | Full control |

---

## Assessment

### Quizzes (230 total questions)

| Quiz | Questions | DCA Domain |
|------|-----------|------------|
| Part 1 | 25 | Installation, Images |
| Part 2 | 30 | Images, Networking, Storage |
| Part 3 | 35 | Orchestration, Security |
| Kubernetes | 20 | Orchestration |
| OpenShift | 25 | Orchestration, Security |
| Storage | 15 | Storage |
| Networking | 20 | Networking |
| Rootless | 15 | Security |
| Security | 20 | Security |
| Operations | 15 | Installation |
| Comparison | 10 | All domains |

### Certification Readiness

- [ ] Score 80%+ on all module quizzes
- [ ] Complete all 9 labs
- [ ] Score 70%+ on practice exams (3 attempts)
- [ ] Review [DCA domain checklist](certification/dca-domain-checklist.md)

---

## External Resources

### Practice Tests

| Resource | Questions | Link |
|----------|-----------|------|
| DCA-Practice-Questions | 333 | [GitHub](https://github.com/lucian-12/DCA-Practice-Questions) |
| ExamTopics | 300+ | [ExamTopics](https://www.examtopics.com/exams/mirantis/dca/view/) |
| Whizlabs Free | 25 | [Whizlabs](https://www.whizlabs.com/blog/docker-certified-associate-exam-questions/) |

### Recommended Reading

- [Docker Deep Dive](https://www.amazon.com/Docker-Deep-Dive-Nigel-Poulton/dp/1916585256) (Nigel Poulton, 2025)
- [Docker Official Documentation](https://docs.docker.com/)
- [Podman Documentation](https://docs.podman.io/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [OpenShift Developer Sandbox](https://developers.redhat.com/developer-sandbox) (Free 30-day access)
- [NIST SP 800-190](https://csrc.nist.gov/publications/detail/sp/800-190/final) (Container Security Guide)

---

## FAQ

**Q: Do I need any prior knowledge?**
A: No. This course assumes zero container experience. Basic command-line familiarity is helpful.

**Q: Should I learn Docker or Podman?**
A: Both! This course teaches both tools side-by-side. Commands are nearly identical, and understanding both makes you more versatile.

**Q: How long does certification take?**
A: With dedicated study, 6-8 weeks following Path C. The exam itself is 90 minutes.

**Q: Is rootless mode important?**
A: Yes. Rootless containers are more secure and increasingly common in enterprise environments. We dedicate an entire module to it.

**Q: What about Kubernetes?**
A: The DCA exam includes Kubernetes basics. Our kubernetes-essentials/ module covers exactly what you need.

**Q: Should I learn OpenShift?**
A: If your organization uses Red Hat products or you want enterprise Kubernetes, yes! OpenShift builds on Kubernetes with additional developer and security features. See the openshift/ module.

---

## Course Design

See [COURSE_DESIGN.md](COURSE_DESIGN.md) for:
- Complete course architecture
- Visual aid specifications
- Source material references
- Assessment strategy

---

## Getting Started

1. **Review prerequisites** in [course_overview.md](course_overview.md)
2. **Choose your learning path** from the options above
3. **Set up your environment** using [Play with Docker](https://labs.play-with-docker.com/) or install locally
4. **Start with concepts/** to build foundational understanding
5. **Track your progress** using the checklists in each module

Ready? Begin with [concepts/01-what-are-containers.md](concepts/01-what-are-containers.md)
