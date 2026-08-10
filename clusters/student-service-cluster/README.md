# Flux Bootstrap

Flux watches `clusters/student-service-cluster` and applies merged git changes.

Before bootstrapping flux, complete the Cilium bootstrap mentioned in [README.md](../../infra/controllers/cilium/README.md).

## Bootstrap

```bash
export GITHUB_TOKEN=<github-pat>
flux bootstrap github --token-auth=true --owner=ssspetrovic \
  --repository=student-service-ops --branch=main \
  --path=clusters/student-service-cluster --personal
```

Create the flux SOPS key after bootstrap:

```bash
kubectl -n flux-system create secret generic sops-age --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

## Check state

```bash
flux check
flux get all -A
```

## Reconcile changes

Merge manifest changes to `main`. After thatm flux deploys shared infrastructure from `infra/`
before the actual workloads from `apps/student-service/`.

To apply a merged change now:

```bash
flux reconcile kustomization flux-system -n flux-system --with-source
```
