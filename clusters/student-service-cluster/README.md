# Flux

This directory is the entrypiont for Flux for the cluster.

## Prerequisites

Before bootstrapping the Flux, there are a couple of steps that are needed to be done:

- the cluster (talos) must be running (flux needs something to run on)
- Cilium needs to be temporarily bootstrapped in order for pods to have networking
- GitHub access token must be created

## Bootstrapping

This cluster was bootstrapped in the following manner:

```bash
export GITHUB_TOKEN=<GH_PAT_TOKEN>

flux bootstrap github \
  --token-auth=true \
  --owner=ssspetrovic \
  --repository=student-service-ops \
  --branch=main \
  --path=clusters/student-service-cluster \
  --personal
```

Because the secrets are SOPS-encrypted in this cluster, Flux also needs a way to decrypt them.
That can be solved by creating the secret from SOPS/AGE key:

```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=age.agekey="$SOPS_AGE_KEY_FILE"
```

Followed by the addition of:

```yaml
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```

## Reconciliation

Flux automatically reconciles and applies changes that get merged into `main`.

The reconciliation can also be triggered manually with:

```bash
flux reconcile ks flux-system -n flux-system --with-source
```

## CHeck state

```bash
flux check
flux get kustomizations -A
flux get helmreleases -A
```
