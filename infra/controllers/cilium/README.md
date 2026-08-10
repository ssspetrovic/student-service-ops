# Cilium

Cilium provides cluster networking and Gateway API support.

## Check state

```bash
kubectl -n kube-system get pods -l app.kubernetes.io/name=cilium
kubectl get gatewayclass
```
