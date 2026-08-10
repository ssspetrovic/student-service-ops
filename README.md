# student-service-ops

This repository manages Student Service infrastructure and Kubernetes
deployments. Flux applies changes merged to `main`.

The cluster has one Talos control-plane node and two workers. Services are
available from the home LAN or Tailscale.

## Main areas

- `talos/`: Talos cluster setup.
- `clusters/`: Flux bootstrap and entrypoints.
- `infra/`: shared cluster services.
- `apps/student-service/`: deployed application workloads.
- `backend/` and `frontend/`: application source.

## Secrets

Secrets use SOPS with age. Set `SOPS_AGE_KEY_FILE` before editing one. Never
commit plaintext secrets, private keys, kubeconfigs, or generated Talos files.

```bash
export SOPS_AGE_KEY_FILE=/path/to/age.key
sops talos/talsecret.sops.yaml
```

## Local checks

```bash
mise install
mise run lint
```
