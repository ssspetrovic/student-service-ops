# Flux Bootstrap

This cluster is bootstrapped from this repository at:

- `clusters/student-service-cluster`

## Bootstrap Steps

Export the GitHub token:

```bash
export GITHUB_TOKEN=<github-pat>
```

Run bootstrap from the repository root:

```bash
flux bootstrap github \
  --token-auth=true \
  --owner=ssspetrovic \
  --repository=student-service-ops \
  --branch=main \
  --path=clusters/student-service-cluster \
  --personal
```

Verify Flux:

```bash
flux check
flux get all -A
```

Create the SOPS age secret for Flux:

```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

Verify the secret exists:

```bash
kubectl -n flux-system get secret sops-age
```
