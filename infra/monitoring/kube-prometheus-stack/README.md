# Monitoring

This folder contains the small monitoring setup for the cluster.
It contains `kube-prometheus-stack` with Prometheus, Grafana, kube-state-metrics, Node Exporter, and Prometheus Operator.

Prometheus collects basic Kubernetes, node, pod, and container metrics.
Grafana shows the built-in dashboards at <https://grafana.student-service.internal>.
Prometheus is not exposed and is within the cluster.

This service keeps 24 hours of metrics in ephemeral storage.
