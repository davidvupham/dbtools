# Observability: Prometheus & Grafana

## Introduction
Observability involves collecting metrics, logs, and traces to understand system state.

## Prometheus
- **Pull Model**: Scrapes metrics from endpoints.
- **PromQL**: Query language for metrics.
- **AlertManager**: Handles alerts.

## Grafana
- **Visualization**: Dashboards for your metrics.
- **Data Sources**: Connects to Prometheus, CloudWatch, etc.

## Setup
Typically deployed via Helm (kube-prometheus-stack).
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack
```
