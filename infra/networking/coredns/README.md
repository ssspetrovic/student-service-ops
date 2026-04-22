# CoreDNS

Managed by Flux from `infra/networking/coredns/`.

Current settings:

- target ConfigMap: `kube-system/coredns`
- plugin: `hosts`
- record: `192.168.1.240 ingress.student-service.internal`
- record: `192.168.1.241 harbor.student-service.internal`

Reconciliation:

- No manual reconcile is required if Flux is already reconciling `infra`.
- To apply the change immediately, reconcile `infra`.

```bash
flux reconcile source git flux-system -n flux-system
flux reconcile kustomization infra -n flux-system
```

Verify:

```bash
kubectl -n kube-system get configmap coredns -o yaml
kubectl -n kube-system get pods -l k8s-app=kube-dns
```
