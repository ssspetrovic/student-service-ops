# Monitoring

There are a couple of parts that go into the whole monitoring stack:

- Prometheus: collects metrics
- Grafana: visualization via dashboards
- Prometheus Operator: manages Prometheus in k8s world
- `kube-state-metrics`: turning k8s object states into metrics - pod states, PVC states, job completions, etc.
- Node Exporter: reports the metrics gatherd from OS and hardware (CPU, memory, etc.). Runs on every node

## Access

To access Grafana, simply open <https://grafana.student-service.internal>/

Grafana admin credentials are stored in a SOPS-encrypted secred.

## Data

Prometheus is currently configured to retain the metrics for 24 hours in the ephemeral storage.
Metrics can get lost if a pods gets restarted due to ephemeral storage nature.

## Check sttae

```bash
kubectl get pods -n monitoring
kubectl get pods -n monitoring-node-exporter
```
