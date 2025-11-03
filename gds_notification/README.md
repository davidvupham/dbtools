# GDS Notification Service

This directory contains the project deliverables for the GDS Notification Service — a highly available service that ingests alert emails, queries a SQL Server stored procedure (or DB) to determine recipients, and forwards alerts to those recipients.

Contents
- `docs/` - requirements, functional spec, design, deployment notes, and SQL data model
- `service/` - FastAPI ingest service stub for PoC
- `worker/` - worker stub to process alert jobs and forward emails
- `docker-compose.yml` - development PoC including MailHog and RabbitMQ
- `requirements.txt` - Python dependencies for the PoC

Purpose
- Consolidate design and project artefacts in one place so implementation, review, and deployment can move forward.

Next steps
- Review the docs in `docs/` and confirm assumptions (especially about webhook vs IMAP ingestion and target hosting).
- I can start implementing the PoC API + worker and run it locally with Docker Compose after you confirm choices.
