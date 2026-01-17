# GitOps with ArgoCD

## Introduction
GitOps uses Git as the single source of truth for infrastructure and applications.

## ArgoCD
- **Declarative**: Syncs K8s state with Git repo.
- **Drift Detection**: Alerts or fixes when live state differs from Git.

## Workflow
1. Developer pushes change to Git (`deployment.yaml`).
2. ArgoCD detects change.
3. ArgoCD syncs cluster to match Git.

## Helm Integration
ArgoCD can manage Helm charts directly.
