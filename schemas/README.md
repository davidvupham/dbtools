# GDS Metrics Schema (Stub)

This folder contains a lightweight Avro schema (`metrics-value.avsc`) for
metric events published to Kafka by `gds_monitor` and consumed by
`gds_alerting`, analytics, and warehousing.

## Subject naming

Use a subject per topic for value schemas, e.g.:
- gds.metrics.postgresql.production-value
- gds.metrics.mongodb.staging-value

Alternatively, use a single shared value subject `gds.metrics.value` if
all metric payloads follow the same structure across database types.

## Compatibility

Set compatibility to `BACKWARD` (or `FULL` if feasible) to allow schema evolution:
- Additive changes only (new optional fields with defaults)
- Do not rename fields or change types without a full migration plan

## Registering the schema (Confluent Schema Registry)

Using curl:

```bash
SCHEMA_REGISTRY_URL=http://localhost:8081
SUBJECT=gds.metrics.value
curl -s -X POST \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @<(jq -n --argfile schema metrics-value.avsc '{schema: $schema|tostring}') \
  "$SCHEMA_REGISTRY_URL/subjects/$SUBJECT/versions"
```

Using Confluent CLI:

```bash
confluent schema-registry schema create \
  --subject gds.metrics.value \
  --schema metrics-value.avsc
```

## Notes

- Timestamps are encoded as ISO-8601 strings to keep examples minimal; you may
  prefer `long` with `timestamp-millis` logical type in production.
- Keep messages small; publish one metric per message for better ordering and
  backpressure handling.
