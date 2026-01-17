# Security in System Design

Security is a foundational pillar of reliable distributed systems (Phase 4: Designing for Trust & Recovery).

## 1. Authentication (AuthN)
*Verifying who the user is.*

- **OAuth 2.0 / OIDC**: Standard for delegated authorization and federated identity.
- **JWT (JSON Web Tokens)**: Stateless authentication; token contains user claims.
- **Session-based**: Stateful; requires server to store session data (e.g., Redis).

## 2. Encryption
*Protecting data confidentiality.*

- **In-Transit**: TLS/SSL (HTTPS) ensures data moving between client/server or service/service cannot be intercepted.
- **At-Rest**: Encrypting data stored in databases or S3 using keys (e.g., AES-256, KMS).

## 3. Access Control (AuthZ)
*Verifying what the user can do.*

- **RBAC (Role-Based Access Control)**: Permissions assigned to roles (Admin, Editor); users assigned to roles. Simple and common.
- **ABAC (Attribute-Based Access Control)**: Permissions based on attributes (user location, time of day, resource sensitivity). More granular but complex.
