# CloudNativePG

Managed by Flux from `infra/controllers/cloudnative-pg/`.

Current paths:

- `infra/controllers/cloudnative-pg/`
- `clusters/student-service-cluster/cloudnative-pg.yaml`

Flux ownership:

- `cloudnative-pg` reconciles `./infra/controllers/cloudnative-pg`
- it depends on the shared `infra` Kustomization

Current settings:

- chart: `cloudnative-pg`
- chart version: `0.29.0`
- application version: `1.30.0`
- namespace: `cnpg-system`
- source: `https://cloudnative-pg.github.io/charts`
- CRDs are managed through the Helm release

This path installs only the operator. PostgreSQL `Cluster` resources belong
under `apps/student-service/` and are reconciled separately.

Verification:

```bash
flux get kustomizations -A
flux get helmreleases -A
kubectl get pods -n cnpg-system
kubectl get crds | rg cnpg.io
```
