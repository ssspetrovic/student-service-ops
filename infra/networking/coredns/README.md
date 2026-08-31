# CoreDNS

CoreDNS allows the workloads inside of the cluster to resolve
the private service names from the [networking overview](../README.md).

In simple terms, the pods ask the CoreDNS the following question: \
"What IP address is `student-service.internal`?"

- CoreDNS responds with `192.168.1.240`

CoreDNS maps the frontend, Harbor and Grafana hostnames to their private LB addresses

## Check state

```bash
kubectl -n kube-system get configmap coredns -o yaml
```
