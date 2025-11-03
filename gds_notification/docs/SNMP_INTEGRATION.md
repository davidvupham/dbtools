# SNMP Trap Integration (SolarWinds DPA)

This document describes how to configure SolarWinds DPA to send SNMP traps to the
GDS Notification Service PoC and how the PoC handles traps.

Local PoC notes
- The PoC container binds an SNMP trap listener to container UDP port 162. The `docker-compose.yml`
  maps host UDP port 1162 to container 162. To test locally, configure DPA (or an SNMP trap sender)
  to send traps to <host-ip>:1162.

What the receiver does
- Receives SNMP traps and extracts varbinds (OID -> value).
- If `snmpTrapOID.0` (OID 1.3.6.1.6.3.1.1.4.1.0) is present, its value is used as `alert_name`.
- Otherwise the receiver falls back to using the first varbind OID as the alert identifier.
- The receiver computes an idempotency id and publishes a normalized JSON payload to the
  RabbitMQ `alerts` queue for the worker to process.

Configure SolarWinds DPA to send SNMP traps
- In DPA alert/contact configuration, add an SNMP trap target pointing to the host running
  this PoC and the chosen port (e.g., 1162).

Security & production notes
- SNMPv1/2 traps are unauthenticated by default. In production, prefer using a secure
  transport (e.g., VPN) or configure network-level ACLs so only DPA hosts can reach the
  trap receiver.
- Consider using SNMPv3 with authentication and encryption; the current PoC listener
  handles traps broadly and would need to be extended to validate SNMPv3 credentials.

Next steps
- If you want SNMPv3 support, I can extend the receiver to require SNMPv3 user/config and
  validate authentication/encryption before accepting traps.
