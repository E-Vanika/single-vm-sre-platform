# Operator runbook

## Before responding

1. Acknowledge the alert and record the start time in UTC.
2. Confirm user impact through the public `/readyz` and one user-facing endpoint.
3. Check whether the alert coincides with a deployment, failure drill, or infrastructure change.
4. Prefer reversible mitigation first; preserve logs and timestamps for later analysis.

## High 5xx rate or fast error-budget burn

**Confirm**

```bash
curl -fsS https://solo-sre-pg.duckdns.org/readyz
docker compose ps
docker compose logs --since 15m app app-2 greeting-service caddy
```

**Diagnose**

- Break errors down by `path` and application process in Grafana.
- Check `docker stats` for CPU or memory pressure.
- Check the greeting dependency if failures are concentrated on `/greet`.
- Compare `/status` with the most recently deployed Git SHA.

**Mitigate**

- If the incident began after a release, run `./scripts/rollback.sh`.
- If one application process is unhealthy, remove or restart only that container while the other continues serving.
- Do not restart every container before collecting logs unless user impact requires immediate restoration.

## High p95 latency or slow error-budget burn

1. Compare request latency with CPU utilization, load, memory pressure, and swap use.
2. Identify whether one route or the downstream greeting service dominates latency.
3. Check Caddy and application logs for retries, timeouts, or upstream failures.
4. If correlated with a release, roll back. If correlated with sustained load, temporarily reduce nonessential traffic and document the capacity limit.

## Application readiness failure

```bash
docker compose ps
docker inspect app --format '{{.State.Status}} {{.State.ExitCode}} {{.RestartCount}}'
docker compose logs --tail 100 app app-2
curl -v http://localhost/readyz
```

- Exit code 137 indicates an OOM kill; correlate it with the memory dashboard.
- Repeated startup errors after a release should trigger `./scripts/rollback.sh`.
- If only one replica fails, keep the healthy replica in service while investigating.

## VM unreachable

1. Test DNS resolution, TCP 443, and SSH separately to identify the failing layer.
2. Check the OCI instance state, VNIC public IP, security list, route table, and internet gateway.
3. Compare cloud resources with Terraform using `terraform plan`; investigate unexpected drift before applying.
4. Use the OCI serial console if the instance is running but SSH is unavailable.
5. Recreate the VM from Terraform and Ansible only after less destructive recovery options are exhausted.

## Metrics missing

```bash
docker compose ps vmagent node-exporter app app-2
docker compose logs --tail 100 vmagent node-exporter
docker exec vmagent wget -qO- http://node-exporter:9100/metrics | head
docker exec vmagent wget -qO- http://app:8000/metrics | head
```

- Confirm all monitored containers share the `internal` network.
- Verify remote-write URL and credentials without printing secret values.
- Distinguish scrape failures from remote-write failures before changing firewall rules.

## Disk pressure

```bash
df -h
docker system df
sudo du -xhd1 /var/lib/docker /var/log 2>/dev/null
```

Delete only identified disposable data. Caddy and container logs are size-bounded; investigate unexpected growth before cleanup.

## After restoration

1. Record detection, acknowledgement, mitigation, and recovery times.
2. Quantify user impact and error-budget consumption.
3. Create a postmortem when impact was material or the failure mode could recur.
4. Assign corrective actions with owners and verification criteria.
