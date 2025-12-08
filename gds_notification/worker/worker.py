#!/usr/bin/env python3
"""
Simple RabbitMQ consumer worker (PoC).

Behavior:
- Waits on queue 'alerts'
- For each message, decodes JSON and simulates a stored-proc call to get recipients
- Sends the alert to recipients via SMTP (MailHog by default)
"""

import json
import logging
import os
import smtplib
import time
from email.message import EmailMessage

import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gds_notification.worker")

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")
SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))


def get_mock_recipients(alert_name, db_instance_id):
    # In a real worker, this would call SQL Server stored proc dbo.GetRecipientsForAlert
    # For PoC we return a small static list or read from env var MOCK_RECIPIENTS as JSON
    env = os.getenv("MOCK_RECIPIENTS")
    if env:
        try:
            return json.loads(env)
        except Exception:
            logger.exception("MOCK_RECIPIENTS is invalid JSON; falling back to default list")
    # default recipients
    return [
        {"recipient_id": 1, "email": "test1@example.com", "name": "Test One"},
        {"recipient_id": 2, "email": "test2@example.com", "name": "Test Two"},
    ]


def send_via_smtp(from_addr, to_addr, subject, body_text):
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject or "Alert"
    msg.set_content(body_text or "")
    with smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT) as s:
        s.send_message(msg)


def on_message(ch, method, properties, body):
    try:
        logger.info("Received message")
        payload = json.loads(body)
        alert_name = payload.get("alert_name")
        db_instance_id = payload.get("db_instance_id")
        subject = payload.get("subject")
        body_text = payload.get("body_text")
        idempotency_id = payload.get("idempotency_id")

        recipients = get_mock_recipients(alert_name, db_instance_id)
        if not recipients:
            logger.warning("No recipients returned for alert %s", alert_name)

        for r in recipients:
            try:
                send_via_smtp("alerts@example.com", r["email"], subject, body_text)
                logger.info("Sent alert to %s", r["email"])
                # In production, persist recipient_send_status as 'sent'
            except Exception:
                logger.exception("Failed to send to %s", r.get("email"))
                # In production, increment attempt_count and possibly requeue or DLQ

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("Processing message failed; will nack and requeue")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    params = pika.URLParameters(RABBIT_URL)
    while True:
        try:
            logger.info("Connecting to RabbitMQ...")
            conn = pika.BlockingConnection(params)
            channel = conn.channel()
            channel.queue_declare(queue="alerts", durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue="alerts", on_message_callback=on_message)
            logger.info("Worker started, waiting for messages...")
            channel.start_consuming()
        except Exception:
            logger.exception("Connection failed, retrying in 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()
