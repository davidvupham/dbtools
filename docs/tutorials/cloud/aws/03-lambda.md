# AWS Lambda & Serverless

## Introduction
Serverless computing lets you run code without provisioning or managing servers.

## Lambda Fundamentals
- **Function**: The code you run.
- **Trigger**: What starts the function (API Gateway, S3 Upload, etc.).
- **Handler**: The entry point in your code.

## Configuration
- **Memory/Timeout**: Adjust based on needs.
- **Environment Variables**: Store config.

## Cold Starts
The delay when a function runs for the first time in a while. Keep this in mind for latency-sensitive apps.
