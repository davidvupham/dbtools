# Python for DevOps Automation

## Introduction
Python is the preferred language for DevOps due to its simplicity and libraries.

## Automation Essentials

### Libraries
- `os` / `sys`: Operating system interaction.
- `subprocess`: Run shell commands.
- `requests`: HTTP library for API interaction.
- `json`: Parsing JSON data.

### AWS SDK (Boto3)
Automate AWS resources.
```python
import boto3

s3 = boto3.client('s3')
response = s3.list_buckets()
print(response['Buckets'])
```

### Error Handling
Always use try-except blocks.
```python
try:
    # automation logic
except Exception as e:
    logging.error(f"Failed: {e}")
```
