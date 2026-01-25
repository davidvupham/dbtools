# Chapter 20: Agent governance

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-4_Agentic_AI-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Implement safety guardrails for production agents
2. Design observability for agent systems
3. Apply human-in-the-loop patterns appropriately
4. Build trust through transparency and auditability

## Table of contents

- [Introduction](#introduction)
- [Safety guardrails](#safety-guardrails)
- [Observability](#observability)
- [Human-in-the-loop](#human-in-the-loop)
- [Auditability](#auditability)
- [Risk management](#risk-management)
- [Governance framework](#governance-framework)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Agents can take autonomous actions—a powerful capability that requires careful governance. This chapter covers patterns for building trustworthy agent systems that organizations can deploy with confidence.

> [!WARNING]
> Agents operating without proper governance can cause data loss, security breaches, or operational incidents. Never deploy agents in production without appropriate safeguards.

[↑ Back to Table of Contents](#table-of-contents)

## Safety guardrails

### Action classification

```python
from enum import Enum, auto


class ActionRisk(Enum):
    READ_ONLY = auto()      # No state changes
    REVERSIBLE = auto()     # Can be undone
    IRREVERSIBLE = auto()   # Cannot be undone


class ActionClassifier:
    """Classify actions by risk level."""

    RISK_MAP = {
        # Read-only actions
        "query_database": ActionRisk.READ_ONLY,
        "get_metrics": ActionRisk.READ_ONLY,
        "read_file": ActionRisk.READ_ONLY,
        "analyze_log": ActionRisk.READ_ONLY,

        # Reversible actions
        "create_index": ActionRisk.REVERSIBLE,
        "update_config": ActionRisk.REVERSIBLE,
        "create_alert": ActionRisk.REVERSIBLE,

        # Irreversible actions
        "delete_data": ActionRisk.IRREVERSIBLE,
        "drop_table": ActionRisk.IRREVERSIBLE,
        "truncate_table": ActionRisk.IRREVERSIBLE,
    }

    @classmethod
    def get_risk(cls, action: str) -> ActionRisk:
        return cls.RISK_MAP.get(action, ActionRisk.IRREVERSIBLE)
```

### Guardrail implementation

```python
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    requires_approval: bool = False


class AgentGuardrails:
    """Enforce safety guardrails on agent actions."""

    def __init__(self):
        self.action_limits = {}
        self.blocked_patterns = [
            r"DROP\s+TABLE",
            r"TRUNCATE",
            r"DELETE\s+FROM\s+\w+\s*$",  # DELETE without WHERE
        ]

    def check_action(self, action: str, arguments: dict) -> GuardrailResult:
        """Check if action is allowed."""
        risk = ActionClassifier.get_risk(action)

        # Block irreversible actions without explicit approval
        if risk == ActionRisk.IRREVERSIBLE:
            return GuardrailResult(
                allowed=False,
                reason=f"Irreversible action '{action}' requires human approval",
                requires_approval=True
            )

        # Check for dangerous patterns in SQL
        if "query" in arguments:
            for pattern in self.blocked_patterns:
                if re.search(pattern, arguments["query"], re.IGNORECASE):
                    return GuardrailResult(
                        allowed=False,
                        reason=f"Query matches blocked pattern: {pattern}"
                    )

        # Check rate limits
        if self._exceeds_limit(action):
            return GuardrailResult(
                allowed=False,
                reason=f"Rate limit exceeded for action '{action}'"
            )

        return GuardrailResult(allowed=True, reason="Passed all checks")

    def _exceeds_limit(self, action: str) -> bool:
        """Check if action exceeds rate limit."""
        # Implementation
        return False


# Usage
guardrails = AgentGuardrails()


async def execute_with_guardrails(action: str, arguments: dict):
    """Execute action with guardrail checks."""
    result = guardrails.check_action(action, arguments)

    if not result.allowed:
        if result.requires_approval:
            approval = await request_human_approval(action, arguments, result.reason)
            if not approval:
                return {"error": "Action denied by human reviewer"}
        else:
            return {"error": result.reason}

    return await execute_action(action, arguments)
```

### Output validation

```python
class OutputValidator:
    """Validate agent outputs before execution."""

    def validate_sql(self, sql: str) -> tuple[bool, str]:
        """Validate SQL before execution."""
        sql_upper = sql.upper().strip()

        # Must be SELECT only
        if not sql_upper.startswith("SELECT"):
            return False, "Only SELECT queries allowed"

        # Check for subqueries with modifications
        if any(kw in sql_upper for kw in ["INSERT", "UPDATE", "DELETE", "DROP"]):
            return False, "Modification keywords not allowed"

        return True, "Valid"

    def validate_file_path(self, path: str) -> tuple[bool, str]:
        """Validate file path for safety."""
        allowed_dirs = ["/var/log/", "/tmp/", "/home/app/"]

        if ".." in path:
            return False, "Path traversal not allowed"

        if not any(path.startswith(d) for d in allowed_dirs):
            return False, f"Path not in allowed directories"

        return True, "Valid"
```

[↑ Back to Table of Contents](#table-of-contents)

## Observability

### Tracing agent execution

```python
import uuid
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AgentTrace:
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    steps: list = field(default_factory=list)
    final_result: str = ""
    error: str | None = None


@dataclass
class TraceStep:
    step_id: str
    action: str
    arguments: dict
    result: str
    duration_ms: float
    timestamp: datetime


class AgentTracer:
    """Trace agent execution for debugging and audit."""

    def __init__(self):
        self.traces: dict[str, AgentTrace] = {}

    def start_trace(self, agent_name: str) -> str:
        """Start a new trace."""
        trace = AgentTrace(agent_name=agent_name)
        self.traces[trace.trace_id] = trace
        return trace.trace_id

    def record_step(
        self,
        trace_id: str,
        action: str,
        arguments: dict,
        result: str,
        duration_ms: float
    ):
        """Record a step in the trace."""
        step = TraceStep(
            step_id=str(uuid.uuid4()),
            action=action,
            arguments=arguments,
            result=result[:1000],  # Truncate large results
            duration_ms=duration_ms,
            timestamp=datetime.now()
        )
        self.traces[trace_id].steps.append(step)

    def end_trace(self, trace_id: str, result: str = "", error: str = None):
        """End a trace."""
        trace = self.traces[trace_id]
        trace.end_time = datetime.now()
        trace.final_result = result
        trace.error = error

    def get_trace(self, trace_id: str) -> AgentTrace:
        """Get a trace by ID."""
        return self.traces.get(trace_id)

    def export_trace(self, trace_id: str) -> dict:
        """Export trace for logging/analysis."""
        trace = self.traces[trace_id]
        return {
            "trace_id": trace.trace_id,
            "agent": trace.agent_name,
            "duration_ms": (trace.end_time - trace.start_time).total_seconds() * 1000,
            "steps": len(trace.steps),
            "success": trace.error is None
        }
```

### Metrics collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
agent_actions_total = Counter(
    'agent_actions_total',
    'Total agent actions',
    ['agent', 'action', 'status']
)

agent_action_duration = Histogram(
    'agent_action_duration_seconds',
    'Agent action duration',
    ['agent', 'action']
)

agent_active_sessions = Gauge(
    'agent_active_sessions',
    'Active agent sessions',
    ['agent']
)


async def execute_with_metrics(agent: str, action: str, arguments: dict):
    """Execute action with metrics."""
    agent_active_sessions.labels(agent=agent).inc()

    try:
        with agent_action_duration.labels(agent=agent, action=action).time():
            result = await execute_action(action, arguments)

        agent_actions_total.labels(
            agent=agent, action=action, status='success'
        ).inc()
        return result

    except Exception as e:
        agent_actions_total.labels(
            agent=agent, action=action, status='error'
        ).inc()
        raise

    finally:
        agent_active_sessions.labels(agent=agent).dec()
```

[↑ Back to Table of Contents](#table-of-contents)

## Human-in-the-loop

### Approval workflows

```python
from enum import Enum
from dataclasses import dataclass


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class ApprovalRequest:
    request_id: str
    action: str
    arguments: dict
    reason: str
    agent: str
    timestamp: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer: str | None = None
    review_notes: str | None = None


class ApprovalManager:
    """Manage human approval workflows."""

    def __init__(self, timeout_seconds: int = 300):
        self.pending: dict[str, ApprovalRequest] = {}
        self.timeout = timeout_seconds

    async def request_approval(
        self,
        action: str,
        arguments: dict,
        reason: str,
        agent: str
    ) -> ApprovalRequest:
        """Create approval request."""
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            action=action,
            arguments=arguments,
            reason=reason,
            agent=agent,
            timestamp=datetime.now()
        )
        self.pending[request.request_id] = request

        # Notify reviewers (implementation depends on your system)
        await self._notify_reviewers(request)

        return request

    async def wait_for_approval(
        self,
        request_id: str
    ) -> tuple[bool, str]:
        """Wait for human approval."""
        start = datetime.now()

        while True:
            request = self.pending.get(request_id)
            if not request:
                return False, "Request not found"

            if request.status == ApprovalStatus.APPROVED:
                return True, request.review_notes or ""

            if request.status == ApprovalStatus.REJECTED:
                return False, request.review_notes or "Rejected"

            # Check timeout
            elapsed = (datetime.now() - start).total_seconds()
            if elapsed > self.timeout:
                request.status = ApprovalStatus.TIMEOUT
                return False, "Approval timeout"

            await asyncio.sleep(1)

    def approve(self, request_id: str, reviewer: str, notes: str = ""):
        """Approve a request."""
        request = self.pending.get(request_id)
        if request:
            request.status = ApprovalStatus.APPROVED
            request.reviewer = reviewer
            request.review_notes = notes

    def reject(self, request_id: str, reviewer: str, notes: str = ""):
        """Reject a request."""
        request = self.pending.get(request_id)
        if request:
            request.status = ApprovalStatus.REJECTED
            request.reviewer = reviewer
            request.review_notes = notes
```

### When to require approval

| Scenario | Require Approval |
|:---------|:-----------------|
| Read-only operations | No |
| Create/modify reversible | Optional (configurable) |
| Delete/drop anything | Yes |
| Configuration changes | Yes (production) |
| Actions affecting users | Yes |
| Cost > threshold | Yes |

[↑ Back to Table of Contents](#table-of-contents)

## Auditability

### Audit log structure

```python
@dataclass
class AuditEntry:
    timestamp: datetime
    trace_id: str
    agent: str
    action: str
    arguments_hash: str  # Hash of arguments for privacy
    result_summary: str
    user_id: str | None
    approval_id: str | None
    source_ip: str | None


class AuditLog:
    """Immutable audit log for agent actions."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def log(self, entry: AuditEntry):
        """Log an audit entry."""
        # Append-only log
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(asdict(entry), default=str) + '\n')

    def query(
        self,
        start_time: datetime,
        end_time: datetime,
        agent: str = None
    ) -> list[AuditEntry]:
        """Query audit log."""
        # Implementation
        pass
```

### Compliance reporting

```python
class ComplianceReporter:
    """Generate compliance reports from audit logs."""

    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Generate compliance report."""
        entries = self.audit_log.query(start_date, end_date)

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_actions": len(entries),
                "by_agent": self._count_by_agent(entries),
                "by_action": self._count_by_action(entries),
                "approval_required": self._count_approvals(entries),
                "rejections": self._count_rejections(entries)
            },
            "high_risk_actions": self._get_high_risk(entries),
            "anomalies": self._detect_anomalies(entries)
        }
```

[↑ Back to Table of Contents](#table-of-contents)

## Risk management

### Risk matrix

| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|
| Data corruption | Medium | High | Read-only tools, approval for writes |
| Runaway costs | Medium | Medium | Rate limits, budget alerts |
| Security breach | Low | High | Input validation, least privilege |
| Service disruption | Medium | High | Staged rollout, kill switch |
| Incorrect outputs | High | Medium | Human review, confidence scores |

### Kill switch implementation

```python
class AgentKillSwitch:
    """Emergency stop for agent operations."""

    def __init__(self):
        self.enabled = True
        self._lock = asyncio.Lock()

    async def check(self) -> bool:
        """Check if agents are allowed to operate."""
        async with self._lock:
            return self.enabled

    async def disable(self, reason: str):
        """Disable all agent operations."""
        async with self._lock:
            self.enabled = False
            await self._notify_all_agents_stop()
            await self._log_kill_switch(reason)

    async def enable(self):
        """Re-enable agent operations."""
        async with self._lock:
            self.enabled = True


# Usage in agent execution
kill_switch = AgentKillSwitch()


async def execute_action_safe(action: str, arguments: dict):
    """Execute with kill switch check."""
    if not await kill_switch.check():
        raise RuntimeError("Agent operations are disabled")

    return await execute_action(action, arguments)
```

[↑ Back to Table of Contents](#table-of-contents)

## Governance framework

### Checklist for production agents

```text
AGENT GOVERNANCE CHECKLIST
══════════════════════════

Safety:
□ Actions classified by risk level
□ Irreversible actions require approval
□ Input validation on all arguments
□ Output validation before execution
□ Rate limits configured
□ Kill switch implemented

Observability:
□ All actions traced with unique IDs
□ Metrics exported (Prometheus/etc.)
□ Logs aggregated and searchable
□ Alerts configured for anomalies
□ Dashboards for monitoring

Human-in-the-Loop:
□ Approval workflow for high-risk actions
□ Escalation paths defined
□ Timeout handling for approvals
□ Reviewer notifications working

Auditability:
□ Immutable audit log
□ All actions logged with context
□ Compliance reports available
□ Retention policy defined

Documentation:
□ Agent capabilities documented
□ Risk assessment completed
□ Runbook for incidents
□ Training for operators
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Safety guardrails prevent dangerous actions through classification and validation
- Observability through tracing and metrics enables debugging and monitoring
- Human-in-the-loop patterns ensure oversight for high-risk operations
- Auditability through immutable logs supports compliance and investigation
- A comprehensive governance framework builds trust for production deployment

## Next steps

You have completed Module 4! Continue to **[Module 5: RAG](../module_5_rag/21_rag_fundamentals.md)** to learn how to ground agents in your organization's knowledge.

Before continuing, complete:
- 📝 **[Module 4 Exercises](./exercises/)**
- 📋 **[Module 4 Quiz](./quiz_module_4.md)**
- 🛠️ **[Project 4: Database Operations Agent](./project_4_db_agent.md)**

[↑ Back to Table of Contents](#table-of-contents)
