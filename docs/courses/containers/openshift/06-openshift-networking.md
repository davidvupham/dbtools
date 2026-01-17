# OpenShift networking

> **Module:** OpenShift | **Level:** Intermediate-Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Understand OpenShift SDN architecture
- Configure Routes for external traffic
- Implement network policies
- Troubleshoot networking issues

---

## OpenShift SDN overview

### Network architecture

```mermaid
graph TB
    subgraph External["External Traffic"]
        Client[Client]
    end

    subgraph OpenShift["OpenShift Cluster"]
        subgraph Router["Router Layer"]
            HAProxy[HAProxy Router]
        end

        subgraph SDN["Software Defined Network"]
            OVN[OVN-Kubernetes]

            subgraph Node1["Node 1"]
                Pod1[Pod A]
                Pod2[Pod B]
            end

            subgraph Node2["Node 2"]
                Pod3[Pod C]
                Pod4[Pod D]
            end
        end

        subgraph Services["Service Layer"]
            ClusterIP[ClusterIP Services]
            NodePort[NodePort Services]
            LB[LoadBalancer Services]
        end
    end

    Client --> HAProxy
    HAProxy --> ClusterIP
    ClusterIP --> Pod1
    ClusterIP --> Pod3
    Pod1 <--> OVN
    Pod2 <--> OVN
    Pod3 <--> OVN
    Pod4 <--> OVN
```

### Network plugins

| Plugin | Description | Use Case |
|--------|-------------|----------|
| **OVN-Kubernetes** | Default in OCP 4.x | Standard deployments |
| **OpenShift SDN** | Legacy plugin | Existing installations |
| **Kuryr** | Neutron integration | OpenStack environments |

---

## Services

### Service types

```yaml
# ClusterIP (default, internal only)
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

```yaml
# NodePort (external via node ports)
apiVersion: v1
kind: Service
metadata:
  name: my-app-nodeport
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

```yaml
# LoadBalancer (cloud provider LB)
apiVersion: v1
kind: Service
metadata:
  name: my-app-lb
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

### Headless services

```yaml
# Headless service (DNS only, no ClusterIP)
apiVersion: v1
kind: Service
metadata:
  name: my-app-headless
spec:
  clusterIP: None
  selector:
    app: my-app
  ports:
    - port: 8080
```

---

## Routes in depth

### Route types comparison

| Type | TLS at Router | TLS to Pod | Use Case |
|------|---------------|------------|----------|
| **Edge** | Yes | No | Most common |
| **Passthrough** | No | Yes | End-to-end TLS |
| **Re-encrypt** | Yes | Yes | High security |

### Edge termination

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: edge-route
spec:
  host: app.example.com
  to:
    kind: Service
    name: my-app
  port:
    targetPort: 8080
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect  # or Allow, None
```

### Passthrough

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: passthrough-route
spec:
  host: secure.example.com
  to:
    kind: Service
    name: my-tls-app
  port:
    targetPort: 8443
  tls:
    termination: passthrough
```

### Re-encrypt

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: reencrypt-route
spec:
  host: secure.example.com
  to:
    kind: Service
    name: my-app
  port:
    targetPort: 8443
  tls:
    termination: reencrypt
    certificate: |
      -----BEGIN CERTIFICATE-----
      ...external cert...
      -----END CERTIFICATE-----
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      ...external key...
      -----END RSA PRIVATE KEY-----
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      ...pod CA cert...
      -----END CERTIFICATE-----
```

### Route annotations

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: my-route
  annotations:
    # Timeout
    haproxy.router.openshift.io/timeout: 60s

    # Rate limiting
    haproxy.router.openshift.io/rate-limit-connections: "true"
    haproxy.router.openshift.io/rate-limit-connections.rate-http: "100"

    # Sticky sessions
    haproxy.router.openshift.io/balance: roundrobin
    haproxy.router.openshift.io/disable_cookies: "false"

    # IP whitelist
    haproxy.router.openshift.io/ip_whitelist: 192.168.1.0/24 10.0.0.0/8

    # HSTS
    haproxy.router.openshift.io/hsts_header: max-age=31536000;includeSubDomains

    # Rewrite target
    haproxy.router.openshift.io/rewrite-target: /
spec:
  host: app.example.com
  to:
    kind: Service
    name: my-app
```

---

## Traffic management

### A/B testing

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ab-route
spec:
  host: app.example.com
  to:
    kind: Service
    name: app-v1
    weight: 90
  alternateBackends:
    - kind: Service
      name: app-v2
      weight: 10
```

```bash
# Adjust weights
oc set route-backends ab-route app-v1=90 app-v2=10

# Check current weights
oc describe route ab-route | grep -A5 "Backends"
```

### Blue-green deployment

```bash
# Deploy green version
oc new-app myapp:green --name=app-green

# Switch route to green
oc patch route my-route -p '{"spec":{"to":{"name":"app-green"}}}'

# Verify
oc describe route my-route

# Rollback to blue
oc patch route my-route -p '{"spec":{"to":{"name":"app-blue"}}}'
```

### Canary deployment

```yaml
# Start with 1% to canary
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: canary-route
spec:
  host: app.example.com
  to:
    kind: Service
    name: app-stable
    weight: 99
  alternateBackends:
    - kind: Service
      name: app-canary
      weight: 1
```

```bash
# Gradually increase canary weight
oc set route-backends canary-route app-stable=95 app-canary=5
oc set route-backends canary-route app-stable=80 app-canary=20
oc set route-backends canary-route app-stable=50 app-canary=50
oc set route-backends canary-route app-stable=0 app-canary=100
```

---

## Ingress vs Routes

### Kubernetes Ingress in OpenShift

```yaml
# Ingress (works but Routes are preferred)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    route.openshift.io/termination: edge
spec:
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 8080
  tls:
    - hosts:
        - app.example.com
      secretName: my-tls-secret
```

### When to use Ingress vs Route

| Feature | Use Route | Use Ingress |
|---------|-----------|-------------|
| Traffic splitting | Yes | Limited |
| Path rewriting | Yes | Limited |
| Kubernetes portability | No | Yes |
| OpenShift features | Full | Partial |

---

## Network policies

### Default deny

```yaml
# Deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

### Allow from same namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
spec:
  podSelector: {}
  ingress:
    - from:
        - podSelector: {}
  policyTypes:
    - Ingress
```

### Allow from specific pods

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
  policyTypes:
    - Ingress
```

### Allow from router (for Routes)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-router
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: ingress
  policyTypes:
    - Ingress
```

### Multi-tier application

```yaml
# Web tier - allows router and API calls to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-policy
spec:
  podSelector:
    matchLabels:
      tier: web
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: ingress
  egress:
    - to:
        - podSelector:
            matchLabels:
              tier: api
      ports:
        - port: 8080
    - to:  # DNS
        - namespaceSelector: {}
      ports:
        - port: 53
          protocol: UDP
  policyTypes:
    - Ingress
    - Egress
---
# API tier - allows web tier
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
spec:
  podSelector:
    matchLabels:
      tier: api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              tier: web
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              tier: database
      ports:
        - port: 5432
    - to:  # DNS
        - namespaceSelector: {}
      ports:
        - port: 53
          protocol: UDP
  policyTypes:
    - Ingress
    - Egress
---
# Database tier - allows API tier only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
spec:
  podSelector:
    matchLabels:
      tier: database
  ingress:
    - from:
        - podSelector:
            matchLabels:
              tier: api
      ports:
        - port: 5432
  policyTypes:
    - Ingress
```

---

## DNS and service discovery

### Cluster DNS

```bash
# Service DNS format
<service>.<namespace>.svc.cluster.local

# Examples
my-app.my-project.svc.cluster.local
postgres.database.svc.cluster.local

# Short names (within same namespace)
my-app
postgres.database
```

### Test DNS resolution

```bash
# From a pod
oc rsh my-pod
nslookup my-service
dig my-service.my-project.svc.cluster.local

# Using debug pod
oc run dns-test --image=registry.access.redhat.com/ubi8/ubi --rm -it -- nslookup my-service
```

---

## Troubleshooting

### Common issues

**Route not accessible:**
```bash
# Check route
oc get route my-route
oc describe route my-route

# Check service
oc get service my-service
oc get endpoints my-service

# Check pods
oc get pods -l app=my-app
```

**Network policy blocking traffic:**
```bash
# List network policies
oc get networkpolicies

# Describe policy
oc describe networkpolicy my-policy

# Test connectivity from pod
oc rsh source-pod curl -v http://target-service:8080
```

**DNS issues:**
```bash
# Check DNS pods
oc get pods -n openshift-dns

# Test DNS from pod
oc debug node/my-node -- chroot /host dig my-service.my-project.svc.cluster.local
```

### Diagnostic commands

```bash
# Check router pods
oc get pods -n openshift-ingress

# Router logs
oc logs -f deployment/router-default -n openshift-ingress

# Check network operator
oc get clusteroperator network
oc describe clusteroperator network

# Network diagnostics
oc adm must-gather --image=registry.redhat.io/openshift4/ose-must-gather
```

---

## Key takeaways

1. **Routes are preferred** over Ingress in OpenShift
2. **Three TLS modes**: edge, passthrough, re-encrypt
3. **Traffic splitting** enables A/B and canary deployments
4. **Network policies** provide micro-segmentation
5. **Allow router traffic** explicitly in network policies
6. **DNS follows** Kubernetes naming conventions

---

## What's next

Learn about Operators and the OperatorHub.

Continue to: [07-operators.md](07-operators.md)
