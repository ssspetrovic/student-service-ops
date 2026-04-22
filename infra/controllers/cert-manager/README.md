# cert-manager

Managed by Flux from `infra/controllers/cert-manager/`.

Current paths:

- `infra/controllers/cert-manager/`
- `clusters/student-service-cluster/cert-manager.yaml`

Flux ownership:

- `cert-manager` reconciles `./infra/controllers/cert-manager`

Current settings:

- chart: `cert-manager`
- version: `1.20.2`
- namespace: `cert-manager`
- source: `https://charts.jetstack.io`
- CRDs are installed through the chart with `crds.enabled: true`

Verification:

```bash
flux get kustomizations -A
flux get helmreleases -A
kubectl get pods -n cert-manager
kubectl get crds | grep cert-manager.io
```
