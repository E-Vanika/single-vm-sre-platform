# 📊 Production Monitoring & Observability

## Security & Infrastructure

### TLS Certificate Automation
Implemented automatic TLS certificate provisioning and renewal using Caddy reverse proxy—demonstrating zero-touch security infrastructure and fully automated certificate lifecycle management. Eliminates manual certificate renewals and reduces security vulnerabilities through continuous automated compliance.

![Certificate Issued](image.png)

---

## Metrics Collection & Aggregation

### VictoriaMetrics Remote Write Mode
Engineered lightweight metrics aggregation and remote storage solution, optimized for resource-constrained environments. Leverages Prometheus exporters to scrape detailed system and application metrics, with remote write capabilities to Grafana Cloud for centralized observability and analytics. Designed to maintain high fidelity monitoring without overloading the 1GB VM, ensuring optimal resource utilization in production environments.

![VictoriaMetrics logs](image-1.png)

---

## Grafana Dashboards: RED & USE Metrics

Built comprehensive observability dashboards using RED (Request, Error, Duration) and USE (Utilization, Saturation, Errors) methodologies to display real-time application and host metrics. These industry-standard frameworks enable rapid diagnosis of performance bottlenecks and system health issues.

### Request Rate by Path (RED Metric)
Developed real-time application throughput visualization tracking requests per second by endpoint. Enables rapid detection of traffic anomalies, unusual load patterns, and performance degradation across service endpoints. Critical metric for understanding user experience and capacity planning.

![Request Rate by Path](image-2.png)

### P95 Latency (RED Metric)
Implemented tail latency monitoring using 95th percentile analysis to accurately capture real user experience without being skewed by outliers. Detects subtle performance degradation early before it impacts user satisfaction and SLA compliance.

![P95 Latency](image-3.png)

### CPU Utilization (USE Metric)
Monitor host CPU consumption across containerized workloads to detect resource saturation and prevent performance throttling. This validates capacity planning and workload optimization under the 1-vCPU constraint without claiming host-level high availability.

![CPU Utilization](image-4.png)

### Memory and Swap Utilization (USE Metric)
Memory-pressure monitoring on the constrained 1GB instance detects leaks, OOM conditions, and swap thrashing. It shows the resource tradeoffs involved in operating several bounded containers on minimal infrastructure.

![Memory and Swap Utilization](image-5.png)

### Container Restart Monitoring
Developed container restart tracking to measure system stability. Container churn serves as a leading indicator of instability, resource starvation, or application crashes and provides an early warning signal for SLO risk.

![Container Restarts](image-6.png)

### Disk I/O and Utilization (USE Metric)
Comprehensive disk consumption and I/O pattern analysis to identify storage saturation and workloads with heavy disk activity. Enables proactive capacity planning and workload optimization to prevent disk-related performance bottlenecks.

![Disk Utilization](image-7.png)

## Chaos Engineering & Resilience Testing

Conducted comprehensive chaos engineering tests to validate system resilience and automatic recovery capabilities in production-like scenarios.

### Application Failure & Recovery
Simulated application-process failure by terminating a container. Docker's restart policy restored the process while the second application container remained available behind Caddy.

![Application terminated](image-8.png)

Successfully brought the application back online automatically through container orchestration restart policies.

![Service recovered](image-9.png)

### Out-of-Memory (OOM) Resilience
Demonstrated automatic container recovery under memory pressure. When the memory limit was exceeded, Docker terminated and restarted the affected container.

![OOM container recovery](image-10.png)

### Observability During Chaos
Grafana dashboards provided real-time visibility throughout the entire chaos engineering test, capturing all system behaviors during failure and recovery scenarios.

![Chaos test monitoring dashboard](image-14.png)

### Distributed Tracing & Performance Analysis
Leveraged distributed tracing infrastructure using OpenTelemetry and Grafana Tempo to identify latency bottlenecks and service dependency chains during stress testing.

![Distributed traces dashboard for latency analysis](image-12.png)

## Microservices Architecture & Horizontal Scaling

Added a small downstream service and a second application process to exercise service dependencies, trace propagation, and process-level load balancing on one host.

### Service Composition
Introduced distributed tracing across the application and greeting service, and deployed `app-2` to demonstrate horizontal process scaling within the explicit limits of one VM.

![list of services status](image-13.png)

### Greeting Service Deployment
Successfully deployed and validated the greeting service microservice. Logs demonstrate clean initialization and proper integration with the centralized logging and tracing infrastructure.

![Greeting service startup logs](image-15.png)

### User-Facing Application
User-facing interface for exercising the instrumented API and downstream service path.

![Application homepage](image-11.png)
