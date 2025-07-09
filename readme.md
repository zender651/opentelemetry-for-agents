#  OpenTelemetry Server for agents

This repository demonstrates how to integrate OpenTelemetry with a Python-based FastAPI application (Notion MCP Server) to collect traces, metrics, and logs.

---

## 📊 Tracer vs Meter – At a Glance

| Feature      | `tracer`                              | `meter`                                |
|--------------|----------------------------------------|-----------------------------------------|
| **Purpose**  | Track request flow (spans/traces)      | Track numeric metrics                   |
| **Granularity** | Per-event (request/task)           | Aggregated over time                    |
| **Exported to** | Jaeger, Zipkin, OTLP, etc.         | Prometheus, OTLP, etc.                  |
| **Data Type** | Spans (with duration)                | Counters, Histograms, etc.              |
| **Use case** | Debugging, latency tracking           | Monitoring, alerting, dashboards        |

---

## 🍞 Baked-In Instrumentation

For full observability:
- Use **tracers** to instrument key functions and generate spans.
- Use **meters** to record numerical values like counters or request duration.
- Export metrics, traces, and logs to a collector.

---

## 📦 Running a Local OpenTelemetry Collector

First, create the file `tmp/otel-collector-config.yaml` with a basic config like:

```yaml
receivers:
  otlp:
    protocols:
      grpc:

exporters:
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [logging]
    metrics:
      receivers: [otlp]
      exporters: [logging]
    logs:
      receivers: [otlp]
      exporters: [logging]
```

## Local collector

```bash
docker run -p 4317:4317 \
  -v $(pwd)/tmp/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
  otel/opentelemetry-collector:latest \
  --config=/etc/otel-collector-config.yaml
```
Dependencies needed to bake 

```bash
pip install fastapi uvicorn opentelemetry-distro
opentelemetry-bootstrap -a install

```


+----------------------+     Traces/Logs     +------------------------+
|  MCP MySQL Server   |  ─────────────────▶ |  OpenTelemetry Collector|
|  (FastAPI + OTEL)   |                    +------------------------+
|  CRUD via Tools     |
+----------▲-----------+                                │
           │ Logs/Traces                                ▼
           │                                +--------------------------+
           │                                |     Custom K3s Controller|
           │                                |  Watches OTEL logs (via  |
           │                                |  Prometheus/Loki, etc.)  |
           │                                |  Deletes MCP pod if rule |
           │                                |  violated (e.g., delete) |
           │                                +--------------------------+
           │
           ▼
   MySQL Service (Docker or K8s)


