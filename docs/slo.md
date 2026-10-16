# Service level objectives and error-budget policy

| Field | Value |
|---|---|
| Service | Single-VM SRE Platform |
| Window | Rolling 30 days |
| Review cadence | Monthly |

**Architecture constraint:** one VM in one availability zone

## Service level indicators

Only user-facing routes participate in the SLO. `/healthz`, `/readyz`, `/metrics`, `/status`, `/docs`, and `/_chaos/*` are excluded so probes and deliberate fault injection do not distort user experience.

| SLI | Definition |
|---|---|
| Availability | Non-5xx requests divided by all requests to user-facing routes |
| Latency | Requests to user-facing routes completed in less than 500 ms divided by all such requests |

HTTP 429 responses are counted as available but unsuccessful capacity signals: the application responded correctly, but demand exceeded its configured rate policy. They are monitored separately.

## Objectives

| Objective | Target | Rationale |
|---|---:|---|
| Availability | 99.0% over 30 days | A single VM and availability zone cannot honestly support a high-availability target |
| Latency | 95% under 500 ms over 30 days | Captures user-visible tail latency while allowing brief contention on burstable compute |

At 99.0% availability, the service may consume 1% of eligible requests as errors during the window. The budget is request-based rather than time-based.

## PromQL

Availability over 30 days:

```promql
1 - (
  sum(increase(http_requests_total{status=~"5..",path!~"/(healthz|readyz|metrics|status|docs|_chaos.*)"}[30d]))
  /
  sum(increase(http_requests_total{path!~"/(healthz|readyz|metrics|status|docs|_chaos.*)"}[30d]))
)
```

P95 latency by route:

```promql
histogram_quantile(
  0.95,
  sum by (le, path) (rate(http_request_duration_seconds_bucket[5m]))
)
```

Availability error-budget burn rate:

```promql
(
  sum(rate(http_requests_total{status=~"5..",path!~"/(healthz|readyz|metrics|status|docs|_chaos.*)"}[1h]))
  /
  sum(rate(http_requests_total{path!~"/(healthz|readyz|metrics|status|docs|_chaos.*)"}[1h]))
) / 0.01
```

## Alert policy

Use paired short and long windows to avoid paging on a momentary spike:

| Severity | Condition | Response |
|---|---|---|
| Page | Burn rate above 14.4x over both 5 minutes and 1 hour | Acknowledge, assess user impact, and follow the error-rate runbook |
| Follow-up | Burn rate above 3x over both 30 minutes and 6 hours | Open a reliability action and investigate during working hours |

Host CPU, memory, swap, and disk alerts are diagnostic signals, not service-level objectives. Pages should be tied to user-visible symptoms whenever possible.

## Error-budget policy

When the 30-day availability budget is exhausted:

1. Pause non-reliability changes to the service.
2. Prioritize the failure mode that consumed the most budget.
3. Complete a blameless postmortem for any material incident.
4. Implement and verify corrective actions before resuming feature changes.
5. Resume normal delivery only when the service is back within objective or an explicit risk decision is documented.

The owner of this repository is the approver and incident commander for this single-operator platform. In a team environment, service owners and product stakeholders would jointly approve the target and policy.

## Supporting resource signals

| Resource | Utilization | Saturation or risk signal |
|---|---|---|
| CPU | `1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))` | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` |
| Memory | `1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)` | Swap use and container OOM/restart events |
| Disk | `1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)` | I/O queue depth and read-only filesystem state |
