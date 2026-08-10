# Flux Bootstrap

Flux watches `clusters/student-service-cluster` and applies merged Git changes.

## Bootstrap

```bash
export GITHUB_TOKEN=<github-pat>
flux bootstrap github --token-auth=true --owner=ssspetrovic \
  --repository=student-service-ops --branch=main \
  --path=clusters/student-service-cluster --personal
```

Create the Flux SOPS key after bootstrap:

```bash
kubectl -n flux-system create secret generic sops-age --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

## Check state

```bash
flux check
flux get all -A
```
