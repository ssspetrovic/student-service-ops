# CoreDNS

Kubernetes CoreDNS keeps these records inline:

- `student-service.internal -> 192.168.1.240`
- `harbor.student-service.internal -> 192.168.1.241`

## Check state

```bash
kubectl -n kube-system get configmap coredns -o yaml
```
