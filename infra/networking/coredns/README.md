# CoreDNS

The `student-service.hosts` key is shared by Kubernetes CoreDNS and the tailnet resolver.

- `student-service.internal -> 192.168.1.240`
- `harbor.student-service.internal -> 192.168.1.241`

Kubernetes CoreDNS still resolves other names normally. The tailnet resolver only handles this domain

## Check state

```bash
kubectl -n kube-system get configmap coredns -o yaml
```
