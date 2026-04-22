# Cilium

Managed by Flux from `infra/controllers/cilium/`.

Current settings:

- chart: `cilium`
- version: `1.19.3`
- `gatewayAPI.enabled: true`
- `kubeProxyReplacement: true`

Verify:

```bash
flux get helmreleases -A
kubectl -n kube-system get pods -l app.kubernetes.io/name=cilium
kubectl get gatewayclass
```
