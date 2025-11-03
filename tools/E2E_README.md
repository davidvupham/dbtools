## E2E helper: tools/e2e_send_and_check.py

Quick reference for running the end-to-end smoke tester that sends an SNMP trap to `gds-snmp-receiver` and polls RabbitMQ for a published message.

Usage (from repo root):

```bash
docker compose -f docker-compose.e2e.yml run --rm snmp-sender python tools/e2e_send_and_check.py
```

Purpose:
- Wait for RabbitMQ to be reachable
- Wait for the `alerts` queue (passive check)
- Ensure `snmptrap` is installed
- Send trap to `gds-snmp-receiver` service name on the compose network
- Poll `alerts` queue for a message (basic_get)

Exit codes:
- 0: success (message received)
- 2: RabbitMQ unreachable within timeout
- 3: failed to send snmptrap (subprocess error)
- 4: no message received from RabbitMQ within poll timeout

If the test fails with 404 NOT_FOUND when checking the queue, ensure the receiver declares the queue at startup or increase the wait timeout in the script.

Tips:
- If you need to test SNMP delivery from the host to the container and you used a non-privileged mapping like `-p 1162:162/udp`, target the host port `1162` for `snmptrap`.
- Check RabbitMQ management UI (default 15672) for queues and messages when running locally: http://localhost:15672/ (guest/guest by default in this example stack).
